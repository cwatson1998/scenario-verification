import numpy as np
import sys
import os

# Ensure the parent directory is in the path before attempting the import
try:
    # This is bad- if we add a util in this directory it will break.
    import compiler.util as cutil
except ModuleNotFoundError:
    # Add the parent directory to sys.path
    sys.path.insert(0, '..')

    # Try the import again
    import compiler.util as cutil
    del sys.path[0]


def save_explicit_summaries(sta_file_path, tra_file_path, error_pred, representative_error_valuation, scenario_var_name='scenario', export_directory=None, export_filename_stem=None, rounding_decimals=3):
    ''' Save explicit matrix representations of scenario summaries.
        Inputs:
            sta_file_path and tra_file_path should be generated by PRISM for the DTMC (.pm file) that contains the
                (already) summarized scenarios. This file must contain multiple scenarios, defined by the value of
                some prism variable (which this function receives as scenario_var_name).
            error_pred : dict(str, int) -> bool is an error predicate. Its input is a dict that represents an valuation of
                the PRISM variables. It cannot depend on the value of scenario_var_name.
                (this might require you to rewrite your prism model so error can be detected the same way in each scenario.)
            representative_error_valuation: dict(str, int) needs to satisfy error_pred and contain a complete valuation of
                all the PRISM variables (except for scenario_var_name). The explicit summaries will quotient all the error
                states together, and this will be their representative.
            export_directory: The directory to save the explicit summaries.
            export_filename_stem: The start of the filename. The human-readable key (which is the same format as a PRISM sta
                file) will be saved with the suffix _SUMMARIES_STATES.txt and the npz file containing the explicit summaries
                will be save with the suffix _SUMMARIES.npz
            rounding_decimals: How much to round each transition probability.
        Saves:
            Human-readable state index to PRISM variable valuation (same format as a .sta file). These are the names
                of the states used in the explicit representations. The error state is the last one.
                This is saved at export_directory/export_filename_stem__SUMMARIES_STATES.txt
            Compressed npz file containing explicit representations of summaries. Contains the following keys:
                states_header: 1D array of strings representing the order of the PRISM variables in the states list.
                states_list: 2D array with n rows. The i^th row represents the i^th state and contains the valuation of 
                    the PRISM variables as they appear in states_header. states_header and states_list are like a .sta 
                    file. The error state is the (n^th) state.
                For each value i of the PRISM variable scenario_var_name:
                    C_i: n x n right-stochastic matrix that describes transition over all states
                    A_i: (n-1)x(n-1) matrix that describes transition from distribution over non-error states to 
                        subdistribution over non-error states
                    b_i: (n-1) vector that describes 1-step probability of error from distribution over non-error states.
                This is saved at export_directory/export_filename_stem__SUMMARIES.npz
        Returns:
            Void
    '''
    # Integrity checks:
    assert scenario_var_name not in representative_error_valuation
    assert error_pred(
        representative_error_valuation), "The supplied canonical_error_valuation does not satisfy error_pred."
    # Set up export locations
    if export_directory is None:
        export_directory = os.path.dirname(sta_file_path)
        print(
            f"User did not supply export_directory. We will export the same directory as sta_file_path, which is {sta_file_path}")
    if export_filename_stem is None:
        export_filename_stem = os.path.basename(sta_file_path).split('.')[0]
        print(
            f"User did not supply export_filename_stem. We will use {export_filename_stem}")
    sta_export_path = os.path.join(
        export_directory, f"{export_filename_stem}_SUMMARIES_STATES.txt")
    tra_export_path = os.path.join(
        export_directory, f"{export_filename_stem}_SUMMARIES.npz")
    # Later on we will make export paths for the transition matrices.

    # Read original state file
    original_cipher = cutil.StateCipher(sta_file_path)
    # Build a transition matrix
    original_n = original_cipher.size()

    system_var_name_list = original_cipher.var_name_list.copy()
    assert scenario_var_name in system_var_name_list, f'Tried to case scenarios on var "{scenario_var_name}" which does not exist in .sta file.'
    system_var_name_list.remove(scenario_var_name)

    # If this throws KeyError, then the user did not include every variable in representative_error_valuation.
    representative_error_valuation_tuple = tuple(
        [representative_error_valuation[var_name] for var_name in system_var_name_list])

    # Quotient by error and project out scenario
    system_state_valuation_tuples = set()
    scenario_values = set()
    for s in original_cipher.states_set():
        valuation = original_cipher.forward_lookup(s)
        scenario_values.add(valuation[scenario_var_name])
        if not error_pred(valuation):
            valuation_tuple = tuple([valuation[var_name]
                                    for var_name in system_var_name_list])
            system_state_valuation_tuples.add(valuation_tuple)
    system_state_valuation_tuples = sorted(list(system_state_valuation_tuples))
    new_state_valuation_tuples = system_state_valuation_tuples.copy()
    new_state_valuation_tuples.append(representative_error_valuation_tuple)
    new_n = len(new_state_valuation_tuples)
    # Write the .sta file (do this here so we can build a new state cipher)
    sta_file_lines = [f"{cutil.string_of_tuple(system_var_name_list)}\n"]
    for s, valuation_tuple in enumerate(new_state_valuation_tuples):
        sta_file_lines.append(
            f"{s}:{cutil.string_of_tuple(valuation_tuple)}\n")
    with open(sta_export_path, 'w') as f:
        f.writelines(sta_file_lines)
    print(
        f"Wrote new state file to {sta_export_path}. State {new_n-1} is the (single) error state.")
    new_cipher = cutil.StateCipher(sta_export_path)
    # Now for each scenario we need to make a transition matrix C. I'll make C first then cut it into A and b.
    # scenario_values is the canonical ordering of the scenarios. It matches the order of C_list

    scenario_values = sorted(list(scenario_values))
    C_list = [np.zeros(shape=(new_n, new_n), dtype=np.float64)
              for _ in scenario_values]

    # Now it is time to fill in the transitions.
    with open(tra_file_path, 'r') as f:
        line0 = next(f)
        assert int(line0.split()[
                   0]) == original_n, "Number of states in .sta and .tra do not match."
        for line in f:
            old_source_s, old_dest_s, prob = line.strip().split()
            prob = float(prob)
            source_valuation = original_cipher.forward_lookup(old_source_s)
            dest_valuation = original_cipher.forward_lookup(old_dest_s)
            assert source_valuation[scenario_var_name] == dest_valuation[
                scenario_var_name], ".tra file contains a transition between scenarios"
            scenario_index = scenario_values.index(
                source_valuation[scenario_var_name])
            if error_pred(source_valuation):
                # We will add transitions from error states later
                continue
            # print(f"debug: source valuation {source_valuation}")
            new_source_s = new_cipher.backward_lookup(source_valuation)
            if error_pred(dest_valuation):
                # Add prob to the error state, which is the last one
                C_list[scenario_index][new_source_s, -
                                       1] = C_list[scenario_index][new_source_s, -1] + prob
            else:
                new_dest_s = new_cipher.backward_lookup(dest_valuation)
                C_list[scenario_index][new_source_s, new_dest_s] = prob
    # Now we have explicit representations for all scenario summaries, but we need to do a bit of postprocessing
    for C in C_list:
        # Error state is absorbing:
        C[-1, -1] = 1
        # Round and make sure everything sums to 1.
        np.round(C, decimals=rounding_decimals, out=C)
        for i in range(new_n):
            diff = 1 - np.sum(C[i, :])
            max_index = np.argmax(C[i])
            C[i][max_index] += diff

    # Now C is correct. We just need to define A and b.
    A_list = [C[:-1, :-1].copy() for C in C_list]
    b_list = [C[:-1, -1].copy() for C in C_list]
    # Now we need to save all of these matrices. I could save them as numpy arrays, but instead I will save as pickle.
    save_dict = {}
    save_dict["states_header"] = np.array(system_var_name_list)
    save_dict["states_list"] = np.array(new_state_valuation_tuples)
    for scenario, C, A, b in zip(scenario_values, C_list, A_list, b_list):
        save_dict[f"C_{scenario}"] = C
        save_dict[f"A_{scenario}"] = A
        save_dict[f"b_{scenario}"] = b
    with open(tra_export_path, 'wb') as f:
        np.savez_compressed(f, **save_dict)


def encode_distribution(explicit_scenarios_path, distribution_over_valuations, subdist_ok=False, tolerance=0.001):
    ''' Encode a distribution expressed in terms of PRISM variables into one expressed in terms of the states found in 
        the npz file at explicit scenarios path. '''
    with open(explicit_scenarios_path, 'rb') as f:
        summaries = np.load(f)
        states_header = summaries['states_header']
        states_list = summaries['states_list']
    # Make a reverse dictionary
    reverse_dict = {tuple(valuation): i for i,
                    valuation in enumerate(states_list)}
    distr = np.zeros(len(states_list)-1, dtype=np.float64)
    for k, prob in distribution_over_valuations:
        if isinstance(k, dict):
            valuation = tuple([k[var] for var in states_header])
        else:
            assert len(k) == len(states_header)
            valuation = tuple(k)
        # Now perform lookup.
        distr[reverse_dict[valuation]] = prob
    total = np.sum(distr)
    if total > 1 + tolerance or total < 0 - tolerance:
        raise ValueError(f"Distribution summed to {total}")
    elif (not subdist_ok) and total < 1 - tolerance:
        raise ValueError(
            f"Distribution summed to {total}, did you mean to allow subdistributions?")
    return distr


def encode_assertion(explicit_scenarios_path, predicate_list, offset_list, quiet=True):
    ''' Encode an assertion as a coefficients matrix and offset vector.
        The assertion must be a conjunction of constraints of the form:
            Pr(predicate) <= offset
        Where predicate is a state predicate.
        This is a special kind affine constraint, where the coefficients need
        to be all 1 or 0. 
        The output of this function can be used to make a polyhedron.
        '''
    with open(explicit_scenarios_path, 'rb') as f:
        summaries = np.load(f)
        states_header = summaries['states_header']
        states_list = summaries['states_list']
    coefficients_matrix = np.zeros(
        shape=(len(predicate_list), len(states_list)-1))
    for state_i, valuation in enumerate(states_list[:-1]):
        val_dict = {h: v for h, v in zip(states_header, valuation)}
        for pred_i, pred in enumerate(predicate_list):
            if pred(val_dict):
                coefficients_matrix[pred_i, state_i] = 1
    if len(predicate_list) == 0:
        print("No predicates supplied to encode assertion")
    if not quiet:
        if len(predicate_list) == 0:
            pass
            # print("No predicates supplied to encode assertion")
        else:
            print("Debug: encode assertion key:" + str(states_header))
            rows, cols = coefficients_matrix.shape
            for i in range(rows):
                print(f"----predicate {i}------")
                for j in range(cols):
                    print(f"{states_list[j]} is {coefficients_matrix[i,j]}")
    return coefficients_matrix, np.asarray(offset_list, dtype=np.float64)
