import os
import subprocess
import re
import tqdm
import matplotlib.pyplot as plt
import numpy as np
import itertools
import random
import pickle
from util import count_leading_spaces, VarValuationDict

# I don't like the following approach to parallelism because I think it has to make
# one python interpreter per worker.
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


def extract_result(text):
    ''' Helper function for reading PRISM's stdout after checking the probability of a PCTL query. '''
    # Regular expression pattern to match "Result: " followed by any non-whitespace characters
    pattern = r"Result:\s*(\S+)"
    match = re.search(pattern, text)

    if match:
        return match.group(1)  # Return the matched string
    else:
        return None


def extract_details(text):
    ''' Written with help from ChatGPT. '''
    keys = ['Time for model construction',
            'States',
            'Transitions',
            'Choices',
            'Time for model checking',
            'Result']
    details_dict = {k: None for k in keys}
    for k in keys:
        match = re.search(rf"{k}:\s*(\S+)", text)
        if match:
            details_dict[k] = match.group(1)
    # Let's manually add in the memory
    units_match = re.search(
        r"TOTAL:\s*\[\s*[\d.]+\s*([A-Za-z]+)\s*\]", text)
    magnitude_match = re.search(r"TOTAL:\s*\[\s*([\d.]+)", text)
    if magnitude_match and units_match:
        magnitude = magnitude_match.group(1)
        units = units_match.group(1)
        if units == "KB":
            scale = 1
        elif units == "MB":
            scale = 1000
        elif units == "GB":
            scale = 1000 * 1000
        else:
            raise ValueError(
                f"We found the illegal memory scale {units} from the result\n{text}")
        details_dict["Memory (KB)"] = float(magnitude) * scale
    else:
        details_dict["Memory (KB)"] = None
    return details_dict


def parse_properties(text: str):
    '''This function written by chatgpt.
        The input is the output of prism when called with a list of properties.
        The output is a list of the properties in order.'''
    # Regex pattern to capture everything after (N) until the newline
    pattern = r"\(\d+\)\s*(.*?)\s*(?=\n|$)"

    # Extract the relevant section starting with "N properties:"
    match = re.search(r"\d+ properties:\n((?:.*\n)*?)(?=\n|[-]{5,})", text)

    if not match:
        return []  # No properties found

    properties_block = match.group(1)

    # Find all properties in the block
    properties = re.findall(pattern, properties_block)

    if len(properties) < 1:
        return None
    else:
        return properties


def extract_details_multiple_properties(text):
    '''Text is the output of PRISM when run with multiple properties'''
    # First, find the list of properties
    property_list = parse_properties(text)
    if property_list is None:
        return [extract_details(text)]
    dashes_pattern = r'[-]{10,}\s*\n'
    segments = re.split(dashes_pattern, text)
    assert len(property_list) + 2 == len(segments)
    details_list = []
    for property, segment in zip(property_list, segments[1:-1]):
        # Ensure the property appears
        assert property.strip() in segment, "Could not find the property in the text output"
        details_list.append(extract_details(segment))
    return details_list


def compute_probability(model_path, formula_path_or_inline, inline_formula=False, return_details_dict=False):
    ''' The naming of these arguments could be improved. '''
    if inline_formula:
        command = [
            "prism",
            model_path,
            '-pf',
            formula_path_or_inline
        ]
    else:
        command = [
            "prism",
            model_path,
            formula_path_or_inline
        ]
    # Run the command
    result = subprocess.run(command, check=True,
                            capture_output=True, text=True)
    if len(result.stderr) > 0:
        print(result.stderr)
    res = extract_result(result.stdout)
    if res is None:
        print("Stdout:")
        print(result.stdout)
        raise ValueError(
            "compute probability failed, likely due to the model being ill formed.")
    if return_details_dict:
        return res, extract_details(result.stdout)
    else:
        return res


def extract_result_with_printall_filter(text, sta_path, interface_vars):
    ''' Extract the result and return as a VarValuationDict.
        -- text is stdout of running a prism command with filter(printall, _, _)
        -- sta_path is path to the .sta file for the prism model.
        -- interface_vars is named suggestively because of my intended use to generate
            summaries. We are projecting out all of the vars that are not in interface_vars.
            This only makes sense if the text only has one result per valuation of interface_vars.
            We will throw ValueError if we find this is not the case. The easy way to enforce
            this is to make the filter used with the command you used to generate the text
            assign a concrete value to every var not in interface_vars. '''
    var_valuation_dict = VarValuationDict(
        sta_path, allow_overwrite=False, fixed_key_vars=interface_vars, project_to_key_vars=True)
    # Now I need to get an iterable of all the matches.
    lines = text.splitlines(keepends=False)

    def parse_string(input_string):
        ''' This helper function written with ChatGPT '''
        # Define the regex pattern
        # pattern = r'(\d+):\((\d+,\d+,\d+)\)=([\S]+)'
        # pattern = r'(\d+):\((\d+(?:,\d+)*)\)=([\S]+)'
        pattern = r'(\d+):\(((-?\d+)(?:,-?\d+)*)\)=([\S]+)'
        # Search for the pattern in the input string
        match = re.search(pattern, input_string)
        if match:
            print("Debug: Match!")
            # Extract the integer before the colon
            integer_before_colon = int(match.group(1))
            # Extract the tuple of integers
            tuple_of_integers = tuple(map(int, match.group(2).split(',')))
            # Extract the string to the right of the equals sign (this is a number)
            string_after_equals = str(match.group(3)).strip()
            return integer_before_colon, tuple_of_integers, float(string_after_equals)
        else:
            return None  # Return None if no match is found
    for line in lines:
        print(f"debug: line is {line}")
        parsed_line = parse_string(line)
        if parsed_line is not None:
            print(f"debug: parsed as {parsed_line[1]}")
            # This contains a valuation for some non-interface vars. I am going to make the
            # VarValuationDict automatically project these out.
            var_valuation_dict.insert(parsed_line[1], parsed_line[2])
    return var_valuation_dict


def compute_probability_from_multiple_states(model_path, sta_path, formula_path_or_inline, filter_formula, inline_formula=False, return_details_dict=False, interface_vars=None):
    '''
        This function computes the value of `formula_path_or_inline' from all initial states in the prism
        file found at `model_path'. For a single initial state, it should return the same result as compute_probability.
        (Though expressed in a different datastructure).
        - model_path: Path to dtmc file (potentially with multiple initial states)
        - sta_path: Path to .sta file for the model.
        - formula_path_or_inline: The PCTL formula to evaluate.
        - filter: The filter to use. When generating summaries, this will characterize the possible start states of a scenario. 
            This will happen to coincide with what I will put in the init..endinit clause when generating summaries.
        - interface_vars: These determine the only variables to pay attention to, which is useful when generating summaries.
            For each valuation of the interface_vars, The filter should accept exactly one state.
        Returns
            - var_value_dict : VarValuationDict. The keys are partial valuations (if interface_vars is not None, they must
                set exactly these) and the value is the result of formula_path_or_inline starting from that state.
    '''
    if return_details_dict:
        raise NotImplementedError("Have not implemented extracting details.")
    if inline_formula:
        command = [
            "prism",
            model_path,
            '-pf',
            f'filter(printall, {formula_path_or_inline}, {filter_formula})'
        ]

    else:
        raise NotImplementedError(
            "Have not implemented support for PCTL files (just inline formulas)")
        command = [
            "prism",
            model_path,
            formula_path_or_inline
        ]
    # Run the command
    result = subprocess.run(command, check=True,
                            capture_output=True, text=True)
    print("debug")
    print(command)
    print(result.stdout)
    if len(result.stderr) > 0:
        print(result.stderr)
    var_value_dict = extract_result_with_printall_filter(
        result.stdout, sta_path, interface_vars=interface_vars)
    assert isinstance(var_value_dict, VarValuationDict)
    if var_value_dict is None:
        print("We failed to parse any data. Dumping stdout:")
        print(result.stdout)
        raise ValueError(
            "compute probability failed, likely due to the model being ill formed.")
    # If we knew the high and low values for the interface vars, we could check for exhaustive coverage.
    return var_value_dict


def compute_multiple_probabilities(model_path, formula_list_path_or_inline, inline_formula=False, return_details_dict_list=False):
    ''' The naming of these arguments could be improved. '''
    if inline_formula:
        command = [
            "prism",
            model_path,
            '-pf',
            formula_list_path_or_inline
        ]
    else:
        command = [
            "prism",
            model_path,
            formula_list_path_or_inline
        ]
    # Run the command
    result = subprocess.run(command, check=True,
                            capture_output=True, text=True)
    if len(result.stderr) > 0:
        print(result.stderr)
    details_list = extract_details_multiple_properties(result.stdout)
    result_list = [d["Result"] for d in details_list]
    if return_details_dict_list:
        return result_list, details_list
    else:
        return result_list


def copy_with_updated_init_state(model_file_path, output_path, init_dict_or_init_formula):
    ''' Copy a prism model with new state initialization.
      - model_file_path: Original prism model.
      - output_path: Path for new model.
      - init_dict_or_init_formula: 
        - if dict: key is the name of a variable appearing in the prism model
            and the value is the desired init value. Must be None if 
        - if string (formula):  A formula that could go in the init .. endinit construct.
    '''
    if isinstance(init_dict_or_init_formula, dict):
        init_dict = init_dict_or_init_formula
        init_formula = None
    else:
        assert isinstance(init_dict_or_init_formula, str)
        init_dict = None
        init_formula = init_dict_or_init_formula
    # The rest of my function is below this line.
    output_lines = []
    modified_variables = set()
    need_to_add_init_formula = init_formula is not None
    with open(model_file_path, 'r') as f:
        for line_i, line in enumerate(f):
            copied_line = False
            comment_split = line.split("//", 2)
            pre_comment = comment_split[0]
            if need_to_add_init_formula and re.search(r'^\s*module\s', line):
                output_lines.append(f"init {init_formula} endinit\n")
                need_to_add_init_formula = False
            if init_dict is not None:
                for var_name, init_value in init_dict.items():
                    search_pattern = rf'^\s*{re.escape(var_name)}\s*:[\s\S]*?init'
                    if re.search(search_pattern, pre_comment):
                        if var_name in modified_variables:
                            raise ValueError(
                                f"Duplicate init of '{var_name}' in line {line_i}")
                        # Now we need to manipulate the line
                        pre_init = pre_comment.rsplit('init', 1)[0]
                        modified_line = f"{pre_init}init {init_value};"
                        if len(comment_split) > 1:
                            modified_line = modified_line + \
                                "//" + comment_split[1]
                        output_lines.append(modified_line)
                        modified_variables.add(var_name)
                        copied_line = True
                        break
            else:
                # Need to remove initialization from all variable declarations.
                search_pattern = rf'^\s*[A-Za-z_][A-Za-z0-9_]*\s*:[\s\S]*?init'
                if re.search(search_pattern, pre_comment):
                    pre_init = pre_comment.rsplit('init', 1)[0].rstrip()
                    modified_line = f"{pre_init};"  # No initialization
                    if len(comment_split) > 1:
                        modified_line = modified_line + "//" + comment_split[1]
                    else:
                        modified_line = modified_line+'\n'
                    output_lines.append(modified_line)
                    copied_line = True
            if not copied_line:
                output_lines.append(line)
    if init_dict is not None:
        not_found_variables = set(
            init_dict.keys()).difference(modified_variables)
        if len(not_found_variables) != 0:
            raise ValueError(
                f"Could not find declarations for variables {not_found_variables} in {model_file_path}")
    if need_to_add_init_formula:
        raise ValueError(
            "Could not add the init formula because we could not find a module declaration to put it before.")
    with open(output_path, 'w') as f:
        f.writelines(output_lines)


def valuation_to_conjunction(var_name_list, valuation, prime_marks=False):
    ''' var_name_list is the key of the variable names, and valuation list is their values.
        format as a prism guard or update clause. '''
    assert len(var_name_list) == len(valuation)
    if len(var_name_list) == 0:
        return 'true'  # true is a PRISM keyword.
    conjunction = ""
    prime = "'" if prime_marks else ""
    for var, val in zip(var_name_list, valuation):
        conjunction = f"{conjunction} & ({var}{prime} = {val})"
    conjunction = conjunction.removeprefix(" & ")
    return conjunction

# A transition is a pair that is a list of guard


def create_summary_using_filter(model_file_path, interface_var_spec, horizon_guard, init_formula, error_guard=None, temp_dir='.', cleanup=True, quiet=True, lower_threshold=1E-20, error_update=None, max_workers=None, rounding_decimals=4):
    ''' This is like create_summary except it uses PRISM's filter function to save computation. 

        The key idea is we copy one dummy model (removing all the initialization from the variab)
        - model_file_path: Points to a .pm dtmc file that does not use init ... endinit for state initialization
        - init_formula: This needs to characterize the initial values of all non-interface variables.

    '''
    unique_temp_string = f"TEMP_{random.randint(1000,9999)}"
    cleanup_list = []
    # First, create the PCTL formulae:
    # Create a canonical ordering of the system_state_spec
    var_name_list = list(interface_var_spec.keys())

    var_low_list = [interface_var_spec[k][0] for k in var_name_list]
    var_high_list = [interface_var_spec[k][1] for k in var_name_list]
    # Generate the ranges
    ranges = [list(range(low, high + 1))
              for low, high in zip(var_low_list, var_high_list)]
    # Generate the cross product (a list containing all valuations of system variables)
    cross_product = list(itertools.product(*ranges))
    # WARNING: This is not robust to file separators
    model_name = model_file_path.split('/')[-1].split('.')[0]
    pctl_formula_list = []
    # Dicts that put values in the interface variables.
    interface_var_valuation_list = []
    for valuation in cross_product:
        # Create and save the PCTL formula
        valuation_string = ""
        pctl_formula = ""
        interface_var_valuation = dict()
        for var_name, value in zip(var_name_list, valuation):
            pctl_formula = f"{pctl_formula} & {var_name} = {value}"
            valuation_string = f"_{valuation_string}_{var_name}_{value}"
            interface_var_valuation[var_name] = value
        interface_var_valuation_list.append(interface_var_valuation)
        pctl_formula = pctl_formula.removeprefix(
            " & ")
        # At this point, pctl formula is a conjunction characterizing the valuation.
        stopping_formula = ""
        if error_guard is None:
            assert error_update is None
            pctl_formula = f"{pctl_formula} & {horizon_guard}"
            stopping_formula = horizon_guard
        elif error_update is None:
            print("Warning: error_guard exists but update does not.")
            print(
                "This is equivalent to providing a horizon guard that is horizon_guard OR error_guard.")
            # This is where error_guard is just another stopping condition.
            pctl_formula = f"{pctl_formula} & (({horizon_guard}) | ({error_guard}))"
            stopping_formula = f"(({horizon_guard}) | ({error_guard}))"
        else:
            # for error, we will just apply the error update. This happens separately, and the error guard
            # supersedes the horizon guard.
            pctl_formula = f"{pctl_formula} & ({horizon_guard}) & ! ({error_guard})"
            stopping_formula = f"(({horizon_guard}) | ({error_guard}))"

        # This ensures we grab the first time the scenario can end.
        pctl_formula = f"P=? [(!({stopping_formula})) U ({pctl_formula})]"

        pctl_formula_list.append(pctl_formula)

    # Since we are using PRISM's filter, we just need to make one new .pm file that is like
    # base.pm except there are many initial states (exactly the possible valuations of the
    # interface variables). We are going to assume that the init_formula does all this.
    multi_init_model_path = f'{temp_dir}/{unique_temp_string}_{model_name}_multi_init.pm'
    multi_init_sta_path = f'{temp_dir}/{unique_temp_string}_{model_name}_multi_init.sta'
    cleanup_list.append(multi_init_model_path)
    cleanup_list.append(multi_init_sta_path)
    assert isinstance(
        init_formula, str), "copy_with_updated_init_state needs a string."
    copy_with_updated_init_state(
        model_file_path, multi_init_model_path, init_formula)
    # Also generate the .sta file:
    sta_command = ['prism', multi_init_model_path,
                   '-exportstates', multi_init_sta_path]
    sta_result = subprocess.run(sta_command, check=True,
                                capture_output=True, text=True)
    if len(sta_result.stderr) > 0:
        print(sta_result.stderr)
    assert os.path.isfile(multi_init_sta_path)

    if error_update is not None:
        num_cols = len(cross_product) + 1
        pctl_error_formula = f"P=? [(!({stopping_formula})) U ({error_guard})]"
    else:
        num_cols = len(cross_product)
    # Now let us make a table for all the probabilities:
    prob_table = [[-1] * num_cols for _ in range(len(cross_product))]
    row_col_cross_product = list(itertools.product(
        range(len(cross_product)), range(num_cols)))
    # This function will compute the value in a cell:

    def calculate_col(col):
        # This calculates all the values that belong in the row.
        # The return type is util.VarValuationDict
        # You can index in using a key that is a dict that is an
        # assignment to the interface variables. These are stored
        # (in the same order as the rows) in interface_var_valuation_list
        if col < len(cross_product):
            pctl = pctl_formula_list[col]
        else:
            pctl = pctl_error_formula

        var_valuation_dict = compute_probability_from_multiple_states(multi_init_model_path, multi_init_sta_path, pctl,
                                                                      init_formula, inline_formula=True, return_details_dict=False, interface_vars=var_name_list)
        return var_valuation_dict
    # Summary commands are PRISM surface syntax that we will return.
    summary_commands = []

    if max_workers is not None and max_workers > 0:
        # First create a table of all the probabilities.
        # The final columns represents the error guard (if it exists)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_col = {executor.submit(
                calculate_col, col): col for col in range(num_cols)}
            for future in as_completed(future_to_col):
                col = future_to_col[future]
                try:
                    var_valuation_dict = future.result()
                    for row_i, row_valuation in enumerate(interface_var_valuation_list):
                        # The row_valuation is well-formed.
                        prob_table[row_i][col] = var_valuation_dict.lookup(
                            row_valuation)
                except Exception as exc:
                    print(
                        f'col {col} of {num_cols} generated an exception: {exc}')
    else:
        # Fill in in singlethreaded manner.
        for col in range(num_cols):
            var_valuation_dict = calculate_col(col)
            print(f"Debug: Finished computing to compute col {col}")
            print(var_valuation_dict.data_dict.keys())
            for row_i, row_valuation in enumerate(interface_var_valuation_list):
                prob_table[row_i][col] = var_valuation_dict.lookup(
                    row_valuation)
    print(
        f"create_summary has successfully computed probabilities and internally stored them in a {len(prob_table)}x{len(prob_table[0])} table.")

    if round:
        # First, round everything to 6 decimal points
        prob_table = np.asarray(prob_table, dtype=np.float64)
        prob_table = np.round(prob_table, decimals=rounding_decimals)
        for i in range(len(prob_table)):
            # This tries to adjust the largest probability to make things sum to 1.
            diff = 1 - np.sum(prob_table[i][:])
            max_idx = np.argmax(prob_table[i][:])
            prob_table[i][max_idx] = prob_table[i][max_idx] + diff

    for source_valuation_i in range(len(cross_product)):
        command = f"[] {valuation_to_conjunction(var_name_list, cross_product[source_valuation_i], prime_marks=False)} -> "
        update = ""
        for target_valuation_i in range(len(cross_product)):
            # prob = compute_probability(
            #     model_path_list[source_valuation_i], pctl_formula_list[target_valuation_i], inline_formula=True)
            prob = prob_table[source_valuation_i][target_valuation_i]
            if (lower_threshold is None) or float(prob) >= float(lower_threshold):
                # Here I am doing something fancy to avoid no-op updates. I could do it more simply
                update_pair_list = [(var, target_val) for var, source_val, target_val in zip(
                    var_name_list, cross_product[source_valuation_i], cross_product[target_valuation_i]) if source_val != target_val]
                if len(update_pair_list) > 0:
                    update_var_name_list, update_valuation = zip(
                        *update_pair_list)
                else:
                    update_var_name_list = update_valuation = []
                update = f"{update} + {prob}: {valuation_to_conjunction(update_var_name_list, update_valuation, prime_marks=True)}"
        if error_update is not None:
            # This means that all the previous update clauses excluded error states.
            # prob = compute_probability(
            #     model_path_list[source_valuation_i], pctl_error_formula, inline_formula=True)
            prob = prob_table[source_valuation_i][len(cross_product)]
            if (lower_threshold is None) or float(prob) >= float(lower_threshold):
                update = f"{update} + {prob}: {error_update}"

        # if error_guard is not None:
        #     prob = compute_probability(model_path_list[source_valuation_i], pctl_error_path)
        #     raise NotImplementedError("I realized this is not what I want.")
        update = update.removeprefix(" + ")
        command = f"{command} {update};"
        if not quiet:
            print(
                f"Progress: {source_valuation_i} of {len(cross_product)}")
            print(command)
        summary_commands.append(command)
    for fpath in cleanup_list:
        os.remove(fpath)
    return summary_commands


def create_summary(model_file_path, interface_var_spec, horizon_guard, error_guard=None, temp_dir='.', cleanup=True, quiet=True, lower_threshold=1E-20, error_update=None, max_workers=None, round=False, rounding_decimals=6, assume_absorbing_exit=False, return_metadata=False, naive=False):
    # TODO: To make this faster, I could use a filter with the "printall" operator. Then I would only need to
    # parallelize over the PCTL formulas, not the initial states. I also would not need to save so many separate
    # model files. https://www.prismmodelchecker.org/manual/PropertySpecification/Filters
    # TODO: Make rounding_decimals replace round (None can mean do not round.)
    # Get rid of the singlethreaded version because it can't round.
    ''' Options of how to treat error state:
        1. Just like any other state. But need to make sure that the horizon guard makes it reasonable.
        If I don't include error states in the spec, then all error states will automatically get deadlocks, which is good.
        So all I have to do is write an error guard with the provisos that:
            1. there does not exist any configuration s such that horizon_guard(s) /\ system_state(s) /\ error_guard(s)
            2. Every horizon_guard x system_state_spec elts + error_guard partation the cylinder of runs. If this
                does not hold, then some commands will not sum to 1. I could revise the code to allow the user to
                specify an else error state.

    '''
    ''' Create a summary.
        - model_file_path: Path to a prism model.
        - interface_var_spec (formerly system_state_spec): dict where each key is a variable that appears in the PRISM model,
            and each key is a pair of low int value and high int value.
            This should also contain the error state.
            If there are error states, no need to include error state in the system_state_spec
        - horizon_guard: A prism expression that evaluates to true when the horizon has been
          reached, expressed as a string. Typical usage is "N = 10" where N is a variable in the non-system state.
          Important: Any state that satisfies horizon_guard must be absorbing in the original modle
        - error_guard: A PCTL state expression that evaluates to true when in an error state.
            Requirement: a value of system state uniquely determines whether we are in an error
            state or not.
            Important: Any state that satisfies error_guard must be absorbing in the original model
        Also important: all trajectories must eventually reach either horizon_guard or error_guard.
        - error_update. If none, then the error must be recoverable from the system state. No special treatment for error,
            except possibly as a stopping condition.
            If not None, then we treat error separately. We will lose all the details from the rest of the system when error is true,
            and transition immediately to error.
        - assume_absorbing_exit: Assumes that any state that satisfies horizon_guard (or error_guard) is absorbing.
            This causes us to use simpler formulae to extract probabilities. I don't know if this increases efficiency.
        prism model that counts the number of steps and 10 is the desired time horizon. Needs to
         be able to be put into a PCTL conjunction.
        TODO: I could optimize this to not save the pctl formulas (i can inline them into the cli commands)
        and I could erase the temporary models (with special init values) one by one.
        This function written with help from ChatGPT. '''
    unique_temp_string = f"TEMP_{random.randint(1000,9999)}"
    cleanup_list = []
    # First, create the PCTL formulae:
    # Create a canonical ordering of the system_state_spec
    var_name_list = list(interface_var_spec.keys())
    # TODO: Consider asserting that the horizon guard is not part of the system state.
    var_low_list = [interface_var_spec[k][0] for k in var_name_list]
    var_high_list = [interface_var_spec[k][1] for k in var_name_list]
    # Generate the ranges
    ranges = [list(range(low, high + 1))
              for low, high in zip(var_low_list, var_high_list)]
    # Generate the cross product (a list containing all valuations of system variables)
    cross_product = list(itertools.product(*ranges))
    # TODO: This is not robust to file separators
    model_name = model_file_path.split('/')[-1].split('.')[0]
    pctl_formula_list = []
    model_path_list = []
    for valuation in cross_product:
        # Create and save the PCTL formula
        valuation_string = ""
        pctl_formula = ""

        for var_name, value in zip(var_name_list, valuation):
            pctl_formula = f"{pctl_formula} & {var_name} = {value}"
            valuation_string = f"_{valuation_string}_{var_name}_{value}"
        pctl_formula = pctl_formula.removeprefix(
            " & ")
        # At this point, pctl formula is a conjunction characterizing the valuation.
        stopping_formula = ""
        if error_guard is None:
            assert error_update is None
            pctl_formula = f"{pctl_formula} & {horizon_guard}"
            stopping_formula = horizon_guard
        elif error_update is None:
            print("Warning: error_guard exists but update does not.")
            print(
                "This is equivalent to providing a horizon guard that is horizon_guard OR error_guard.")
            # This is where error_guard is just another stopping condition.
            pctl_formula = f"{pctl_formula} & (({horizon_guard}) | ({error_guard}))"
            stopping_formula = f"(({horizon_guard}) | ({error_guard}))"
        else:
            # for error, we will just apply the error update. This happens separately, and the error guard
            # supersedes the horizon guard.
            pctl_formula = f"{pctl_formula} & ({horizon_guard}) & ! ({error_guard})"
            stopping_formula = f"(({horizon_guard}) | ({error_guard}))"
        if assume_absorbing_exit:
            pctl_formula = f"P=? [ F ({pctl_formula}) ]"
        else:
            # This ensures we grab the first time the scenario can end.
            pctl_formula = f"P=? [(!({stopping_formula})) U ({pctl_formula})]"

        pctl_formula_list.append(pctl_formula)
        if not quiet:
            print(pctl_formula)

        # TODO: Why do I make a new .pm file instead of asking the existing .pm file to start from a different initial state?
        # I could make this more efficient using PRISM's filter functionality.

        # Create and save the initial distribution file.
        init_dict = {var_name: value for var_name,
                     value in zip(var_name_list, valuation)}
        updated_model_path = f'{temp_dir}/{unique_temp_string}_{model_name}{valuation_string}.pm'
        model_path_list.append(updated_model_path)
        cleanup_list.append(updated_model_path)
        copy_with_updated_init_state(
            model_file_path, updated_model_path, init_dict)
    if error_update is not None:
        num_cols = len(cross_product) + 1
        if assume_absorbing_exit:
            pctl_error_formula = f"P=? [F ({error_guard})]"
        else:
            pctl_error_formula = f"P=? [(!({stopping_formula})) U ({error_guard})]"
    else:
        num_cols = len(cross_product)
    summary_commands = []
    # First create a table of all the probabilities.
    # The final column represents the error guard.
    prob_table = [[-1] * num_cols for _ in range(len(cross_product))]
    model_construction_time_table = [
        [-1] * num_cols for _ in range(len(cross_product))]
    model_checking_time_table = [
        [-1] * num_cols for _ in range(len(cross_product))]

    row_col_cross_product = list(itertools.product(
        range(len(cross_product)), range(num_cols)))

    def calculate_prob(row, col):
        if col < len(cross_product):
            pctl = pctl_formula_list[col]
        else:
            pctl = pctl_error_formula
        return compute_probability(model_path_list[row], pctl, inline_formula=True)

    def calculate_prob_and_details(row, col):
        if col < len(cross_product):
            pctl = pctl_formula_list[col]
        else:
            pctl = pctl_error_formula
        prob, details_dict = compute_probability(
            model_path_list[row], pctl, inline_formula=True, return_details_dict=True)
        return prob, details_dict

    col_property_list_string = ""
    for formula in pctl_formula_list:
        col_property_list_string = f"{col_property_list_string} ; {formula}"
    if num_cols > len(cross_product):
        col_property_list_string = f"{col_property_list_string} ; {pctl_error_formula}"
    col_property_list_string = col_property_list_string.lstrip(" ; ")

    def calculate_row_probs_and_details(row):
        results_list, details_list = compute_multiple_probabilities(
            model_path_list[row],
            col_property_list_string,
            inline_formula=True,
            return_details_dict_list=True
        )
        return results_list, details_list
    if max_workers is not None and max_workers > 0:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            if naive:
                future_to_row_col = {executor.submit(calculate_prob_and_details if return_metadata else calculate_prob, row, col): (
                    row, col) for row, col in row_col_cross_product}
                for future in as_completed(future_to_row_col):
                    row, col = future_to_row_col[future]
                    try:
                        if return_metadata:
                            result, ddict = future.result()
                            prob_table[row][col] = result
                            model_construction_time_table[row][col] = ddict['Time for model construction']
                            model_checking_time_table[row][col] = ddict['Time for model checking']
                        else:
                            result = future.result()
                            prob_table[row][col] = result
                    except Exception as exc:
                        print(f'{row},{col} generated an exception: {exc}')
            else:
                print("DEBUG: here")
                future_to_row = {executor.submit(calculate_row_probs_and_details, row): (
                    row) for row in range(len(cross_product))}
                for future in as_completed(future_to_row):
                    row = future_to_row[future]
                    try:
                        if return_metadata:
                            results, ddicts = future.result()
                            for col, (result, ddict) in enumerate(zip(results, ddicts)):
                                prob_table[row][col] = result
                                model_construction_time_table[row][col] = ddict['Time for model construction']
                                model_checking_time_table[row][col] = ddict['Time for model checking']
                        else:
                            results, ddicts = future.result()
                            for col, (result, ddict) in enumerate(zip(results, ddicts)):
                                prob_table[row][col] = result
                                # model_construction_time_table[row][col] = ddict['Time for model construction']
                                # model_checking_time_table[row][col] = ddict['Time for model checking']
                    except Exception as exc:
                        print(f'{row} generated an exception: {exc}')

    else:  # No multithreading
        print("DEBUG: no multithreading")
        assert not naive, "Have not implemented naive approach for non-multithreaded."
        for row in tqdm(range(len(cross_product))):
            try:
                if return_metadata:
                    results, ddicts = calculate_row_probs_and_details(row)
                    for col, (result, ddict) in enumerate(zip(results, ddicts)):
                        prob_table[row][col] = result
                        model_construction_time_table[row][col] = ddict['Time for model construction']
                        model_checking_time_table[row][col] = ddict['Time for model checking']
                else:
                    results, ddicts = calculate_row_probs_and_details(row)
                    for col, (result, ddict) in enumerate(zip(results, ddicts)):
                        prob_table[row][col] = result
                        # model_construction_time_table[row][col] = ddict['Time for model construction']
                        # model_checking_time_table[row][col] = ddict['Time for model checking']
            except Exception as exc:
                print(f'{row} generated an exception: {exc}')
            row = calculate_row_probs_and_details(row)
    # Summary table generation complete
    print(
        f"create_summary has successfully computed probabilities and internally stored them in a {len(prob_table)}x{len(prob_table[0])} table.")
    if round:
        # First, round everything to 6 decimal points
        prob_table = np.asarray(prob_table, dtype=np.float64)
        prob_table = np.round(prob_table, decimals=rounding_decimals)
        for i in range(len(prob_table)):
            # This tries to adjust the largest probability to make things sum to 1.
            diff = 1 - np.sum(prob_table[i][:])
            max_idx = np.argmax(prob_table[i][:])
            prob_table[i][max_idx] = prob_table[i][max_idx] + diff

    for source_valuation_i in range(len(cross_product)):
        command = f"[] {valuation_to_conjunction(var_name_list, cross_product[source_valuation_i], prime_marks=False)} -> "
        update = ""
        for target_valuation_i in range(len(cross_product)):
            # prob = compute_probability(
            #     model_path_list[source_valuation_i], pctl_formula_list[target_valuation_i], inline_formula=True)
            prob = prob_table[source_valuation_i][target_valuation_i]
            if (lower_threshold is None) or float(prob) >= float(lower_threshold):
                # Here I am doing something fancy to avoid no-op updates. I could do it more simply
                update_pair_list = [(var, target_val) for var, source_val, target_val in zip(
                    var_name_list, cross_product[source_valuation_i], cross_product[target_valuation_i]) if source_val != target_val]
                if len(update_pair_list) > 0:
                    update_var_name_list, update_valuation = zip(
                        *update_pair_list)
                else:
                    update_var_name_list = update_valuation = []
                update = f"{update} + {prob}: {valuation_to_conjunction(update_var_name_list, update_valuation, prime_marks=True)}"
        if error_update is not None:
            # This means that all the previous update clauses excluded error states.
            # prob = compute_probability(
            #     model_path_list[source_valuation_i], pctl_error_formula, inline_formula=True)
            prob = prob_table[source_valuation_i][len(cross_product)]
            if (lower_threshold is None) or float(prob) >= float(lower_threshold):
                update = f"{update} + {prob}: {error_update}"

        # if error_guard is not None:
        #     prob = compute_probability(model_path_list[source_valuation_i], pctl_error_path)
        #     raise NotImplementedError("I realized this is not what I want.")
        update = update.removeprefix(" + ")
        command = f"{command} {update};"
        if not quiet:
            print(
                f"Progress: {source_valuation_i} of {len(cross_product)}")
            print(command)
        summary_commands.append(command)
    # else: # This is old code to not use multithreading.
    #     print("Warning: not using multithreading is deprecated, and cannot round the probabilities and make the sum to 1.")
    #     # The original way the code works. Synchronous.
    #     for source_valuation_i in range(len(cross_product)):
    #         command = f"[] {valuation_to_conjunction(var_name_list, cross_product[source_valuation_i], prime_marks=False)} -> "
    #         # TODO: Rather than always updating the comand string, I should store these values in a dict so I can massage
    #         # them to make them sum to 1 if they fail to for numerical reasons. I can also catch bugs (that seem to be
    #         # able to arise when there exists a state that satisfies horizon guard or error guard that is not absorbing.)
    #         update = ""
    #         for target_valuation_i in range(len(cross_product)):
    #             prob = compute_probability(
    #                 model_path_list[source_valuation_i], pctl_formula_list[target_valuation_i], inline_formula=True)
    #             if (lower_threshold is None) or float(prob) >= float(lower_threshold):

    #                 update_pair_list = [(var, target_val) for var, source_val, target_val in zip(
    #                     var_name_list, cross_product[source_valuation_i], cross_product[target_valuation_i]) if source_val != target_val]
    #                 if len(update_pair_list) > 0:
    #                     update_var_name_list, update_valuation = zip(
    #                         *update_pair_list)
    #                 else:
    #                     update_var_name_list = update_valuation = []
    #                 update = f"{update} + {prob}: {valuation_to_conjunction(update_var_name_list, update_valuation, prime_marks=True)}"
    #         if error_update is not None:
    #             # This means that all the previous update clauses excluded error states.
    #             prob = compute_probability(
    #                 model_path_list[source_valuation_i], pctl_error_formula, inline_formula=True)
    #             if (lower_threshold is None) or float(prob) >= float(lower_threshold):
    #                 update = f"{update} + {prob}: {error_update}"

    #         update = update.removeprefix(" + ")
    #         command = f"{command} {update};"
    #         if not quiet:
    #             print(
    #                 f"Progress: {source_valuation_i} of {len(cross_product)}")
    #             print(command)
    #         summary_commands.append(command)
    if cleanup:
        for fpath in cleanup_list:
            os.remove(fpath)
    if return_metadata:
        metadata = {'valuation_list': cross_product,
                    'model_construction_time_table': model_construction_time_table,
                    'model_checking_time_table': model_checking_time_table}
        return summary_commands, metadata
    else:
        return summary_commands


def save_summaries(model_file_path, interface_var_spec, horizon_guard, output_file_path, error_guard=None, temp_dir='.', cleanup=True, quiet=True, lower_threshold=1E-20, error_update=None, max_workers=None, round=False, rounding_decimals=6, assume_absorbing_exit=False, use_filter=False, init_formula=None, metadata_path=None):
    # This is going to generate summaries
    # The only state variables present are the ones in system state spec.
    # The initial values are the same as in model_file_path.
    # If use_filter: Importantly, for every valuation to the interface_vars (allowed by the interface_var_spec) there must be
    #     exactly one extension to a valuation to all the prism variables that satisfies init_formula. In other words,
    #     the init formula defines the initial values of all the non-interface vars.

    # This is not a very sophisticated check.
    assert model_file_path != output_file_path
    if use_filter:
        assert init_formula is not None, "To use a filter you need an init formula."
        # Importantly, for every valuation to the interface_vars (allowed by the interface_var_spec) there must be
        # exactly one extension to a valuation to all the prism variables that satisfies init_formula. In other words,
        # the init formula defines the initial values of all the non-interface vars.
        summary_command_list = create_summary_using_filter(model_file_path, interface_var_spec, horizon_guard, init_formula,
                                                           error_guard=error_guard, temp_dir=temp_dir, cleanup=cleanup,
                                                           quiet=quiet, lower_threshold=lower_threshold, error_update=error_update,
                                                           max_workers=max_workers, rounding_decimals=rounding_decimals)
    else:
        assert init_formula is None, "Init formula is to define multiple initial states, but the non-filter way just does this by using multiple files."
        summary_command_list, metadata = create_summary(model_file_path, interface_var_spec, horizon_guard, error_guard=error_guard,
                                                        temp_dir=temp_dir, cleanup=cleanup, quiet=quiet, lower_threshold=lower_threshold, error_update=error_update, max_workers=max_workers,
                                                        round=round, rounding_decimals=rounding_decimals, assume_absorbing_exit=assume_absorbing_exit, return_metadata=True)
    output_lines = []
    with open(model_file_path, 'r') as f:
        # This is adapted from copy_with_updated_init_state
        copied_init_vars = set()
        copied_commands = False
        for line in f:
            should_copy = True
            comment_split = line.split("//", 2)
            pre_comment = comment_split[0]
            # First, check to see if it is an init
            if re.search(rf':[\s\S]*?init', pre_comment):
                # Only copy an init if it is for a system state.
                should_copy = False
                for var_name in interface_var_spec.keys():
                    search_pattern = rf'^\s*{re.escape(var_name)}\s*:[\s\S]*?init'
                    if re.search(search_pattern, pre_comment):
                        should_copy = True
                        copied_init_vars.add(var_name)
                        break
            # Second, check to see if it is a command:
            if "->" in pre_comment:
                should_copy = False
                if not copied_commands:
                    padding = " " * count_leading_spaces(pre_comment)
                    for c in summary_command_list:
                        output_lines.append(f"{padding}{c}\n")
                    copied_commands = True
            elif "+" in pre_comment or '[]' in pre_comment:
                should_copy = False
            if should_copy:
                output_lines.append(line)
    not_found_variables = set(interface_var_spec.keys()
                              ).difference(copied_init_vars)
    if len(not_found_variables) != 0:
        raise ValueError(
            f"Could not find declarations for variables {not_found_variables} in {model_file_path}")
    with open(output_file_path, 'w') as f:
        f.writelines(output_lines)
    if metadata_path is not None:
        print("trying to dump metadata")
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)


# Example usage:
    # model_file_path = './joint_pa/taxinet_Boeing5bins_day_and_night_joint.pm'
    # output_file_path = './taxinet_Boeing5bins_day_and_night_joint_summarized.pm'
    # system_state_spec = {'scenario': (0,1), 'cte': (-1,4), 'he': (-1,2)}
    # horizon_guard = "k = N"
    # error_guard = "cte < 0 | he < 0"
    # temp_dir = './joint_pa'

    # save_summaries(model_file_path, system_state_spec, horizon_guard, output_file_path, error_guard=error_guard, temp_dir=temp_dir, cleanup=True, quiet=False)
