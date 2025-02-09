import subprocess
import re


### Data structures ###

class Bidict():
    # Invariant: Values are unique
    def __init__(self, forward_dict=None):
        ''' We perform a copy of forward_dict. '''
        forward_dict = dict() if forward_dict is None else forward_dict
        self.backward_dict = dict()
        for x, y in forward_dict.items():
            if y in self.backward_dict:
                raise ValueError(
                    f"init_dict is not bijective, viz. ({x}: {forward_dict[x]}) and ({x}: {y})")
            self.backward_dict[y] = x
        # Performing a copy
        self.forward_dict = dict()
        for y, x in self.backward_dict.items():
            self.forward_dict[x] = y

    def insert(self, x, y):
        # For now, I am not allowing re-assignment, although theoretically that could be ok if
        # we check that the invariant is preserved.
        if x in self.forward_dict:
            raise ValueError(
                f"Tried to insert {x}:{y} but the pair {x}:{self.forward_dict[x]} already exists.")
        if x in self.backward_dict:
            raise ValueError(
                f"Tried to insert {x}:{y} but the pair {x}:{self.forward_dict[y]} already exists.")

    def integrity_check(self):
        for x, y in self.forward_dict.items():
            assert self.backward_dict[y] == x
        for y, x in self.backward_dict.items():
            assert self.forward_dict[x] == y

    def forward_lookup(self, x):
        return self.forward_dict[x]

    def backward_lookup(self, y):
        return self.backward_dict[y]

    def x_set(self):
        return set(self.forward_dict.keys())

    def y_set(self):
        return set(self.forward_dict.values())

    def size(self):
        return len(self.forward_dict.keys())


### String manipulation ####

def splice_string(base_string, substring, addition, after=True):
    ''' Splice addition into base_string after (or before) the first
        occurence of substring. '''
    idx = base_string.find(substring)
    if idx == -1:
        raise ValueError(
            f"{substring} does not occur in {base_string} so splicing failed.")
    if after:
        idx += len(substring)
    return base_string[:idx] + addition + base_string[idx:]


def splice_string_all(base_string, substring, addition, after=True):
    ''' Splice in for all occurrences. '''
    if len(substring.strip()) == 0:
        raise ValueError("Cannot splice on a whitespace pattern.")
    components = list(base_string.split(substring))
    if after:
        splice = substring + addition
    else:
        splice = addition + substring
    new_string = components[0]
    for c in components[1:]:
        new_string += splice + c
    # new_string += components[-1]
    return new_string


def count_leading_spaces(string):
    for i, c in enumerate(string):
        if c != ' ':
            return i


def group_by_parens(token_list):
    ''' Given a flat token list, return a list of token lists grouped according to parenthesization 
        Only groups by toplevel parens!
        Gets rid of the toplevel parens. '''
    output_list = []
    open_counter = 0
    for i, t in enumerate(token_list):
        if open_counter == 0 and t == '(':
            output_list.append([])
            open_counter += 1
        elif open_counter == 0:
            raise ValueError(
                f"Expected ( as token {i} of {token_list}.\n Look at our language defn- we are very picky about parentheses!")
        # open_counter >1 0
        elif t == '(':
            output_list[-1].append(t)
            open_counter += 1
        elif open_counter == 1 and t == ')':
            open_counter -= 1
        elif t == ')':
            output_list[-1].append(t)
            open_counter -= 1
        else:
            output_list[-1].append(t)
    return output_list


def strip_outer_parens(token_list):
    grouped = group_by_parens(token_list)
    if len(grouped) != 1:
        raise ValueError(
            f"The token list:\n{token_list}\nwas expected to be wrapped by parentheses.")
    return grouped[0]


def string_of_tuple(tuple_or_list):
    ''' Format tuple without extra whitespace. '''
    acc = "("
    for e in tuple_or_list:
        acc = f"{acc}{e},"
    acc = acc.rstrip(',')
    return f"{acc})"

### PRISM specific ####


class StateCipher():
    def __init__(self, state_file_path, quiet=True):
        with open(state_file_path, 'r') as f:
            # var_name_list is public, do not alter implementation.
            self.var_name_list = next(f).strip().removeprefix(
                '(').removesuffix(')').split(',')
            forward_dict = dict()
            for line in f:
                s_str, vars_str = line.strip().split(':')
                var_list = vars_str.removeprefix(
                    '(').removesuffix(')').split(',')
                var_list = [int(var_val) for var_val in var_list]
                forward_dict[int(s_str)] = tuple(var_list)
        self.bidict = Bidict(forward_dict=forward_dict)
        if not quiet:
            print(
                f"Loaded {self.bidict.size()} states with variables {self.var_name_list}")

    def forward_lookup(self, s):
        ''' From the int value of the state to the var_name: value dict.
            Returns a (new) dict representing the valuation. '''
        var_tuple = self.bidict.forward_lookup(int(s))
        # Must be fresh dict, because caller may wish to mutate.
        return {var_name: val for (var_name, val) in zip(self.var_name_list, var_tuple)}

    def backward_lookup(self, var_values):
        if isinstance(var_values, dict):
            # This should implicitly project out keys that do not appear in self.var_name_list.
            var_tuple = tuple([var_values[var_name]
                              for var_name in self.var_name_list])
        elif isinstance(var_values, tuple):
            # Superuser feature, must be in canonical order.
            assert len(var_values) == len(self.var_name_list)
            var_tuple = var_values
        else:
            raise ValueError(
                f"Found type {type(var_values)} but expected var_name:value dict.")
        var_tuple = tuple(var_tuple)
        return self.bidict.backward_lookup(var_tuple)

    def size(self):
        return self.bidict.size()

    def states_set(self):
        return self.bidict.x_set()


class VarValuationDict():
    ''' This is like a dict, except the keys are (potentially partial) valuations. '''

    def __init__(self, state_file_path, quiet=True, allow_overwrite=False, fixed_key_vars=None, project_to_key_vars=True):
        '''
            - fixed_key_vars is just to enforce that every entry key has valuation for exactly these vars.
            - project_to_key_vars: If values for other vars are provided upon insertion, we will project them out.


        '''
        self.state_cipher = StateCipher(state_file_path, quiet=quiet)
        var_name_to_position = {var_name: i for i, var_name in enumerate(
            self.state_cipher.var_name_list)}
        self.var_name_to_position_bidict = Bidict(var_name_to_position)
        # The cipher is mostly used for the canonical ordering of the var_names.
        # The keys in this dict will be tuples, in the order of self.state_cipher.var_name_list.
        # None represents no-assignment to that variable.
        self.data_dict = dict()
        self.allow_overwrite = allow_overwrite
        if fixed_key_vars is not None:
            self.fixed_key_vars_set = set(fixed_key_vars)
            assert self.fixed_key_vars_set.issubset(
                self.state_cipher.var_name_list)
            # Make fixed_key_vars indices
            self.fixed_key_vars_indices = {
                var_name_to_position[var_name] for var_name in self.fixed_key_vars_set}
        else:
            self.fixed_key_vars_set = None
            self.fixed_key_vars_indices = None

    def key_var_value_dict_to_key_tuple(self, key_var_value_dict):
        if self.fixed_key_vars_set is None:
            # It would be ok to replace this check with pass.
            assert set(key_var_value_dict.keys()).issubset(
                self.state_cipher.var_name_list)
        else:
            assert set(key_var_value_dict.keys()) == self.fixed_key_vars_set
        key = []
        for var_name in self.state_cipher.var_name_list:
            try:
                key.append(key_var_value_dict[var_name])
            except KeyError:
                key.append(None)
        key = tuple(key)
        return key

    def project_key(self, key):
        if (not self.project_key) or (self.fixed_key_vars_indices is None):
            return key
        assert isinstance(key, tuple)
        projected_key = [
            key[i] if i in self.fixed_key_vars_indices else None for i in range(len(key))]
        return tuple(projected_key)

    def check_key(self, key):
        ''' Check key (in tuple form) for validity.
            Right now, raises ValueError rather than return bool.'''
        if self.fixed_key_vars_indices is None:
            return
        key_indices = {i for i, val in enumerate(key) if val is not None}
        if key_indices != self.fixed_key_vars_indices:
            raise ValueError(
                f"The provided key {key} had valuations outside of the fixed var indices {self.fixed_key_vars_indices}")
        return

    def insert(self, key_as_dict_or_tuple, value):
        ''' 
            - key_as_dict_or_tuple is a partial valuation of the variables. This serves as the key.
                If you know the canonical order of the variables (as determined by the .sta file used
                to construct this object, it can be a tuple of that order. Use None to denote lack of
                valuation for a variable.
                Otherwise it should be a dict where keys are the names of the Prism variables.)
            - value is value to be stored
        '''
        if isinstance(key_as_dict_or_tuple, dict):
            key = self.key_var_value_dict_to_key_tuple(key_as_dict_or_tuple)
        else:
            assert isinstance(
                key_as_dict_or_tuple, tuple), f'Found type {type(key_as_dict_or_tuple)} but must be dict or tuple.'
            key = key_as_dict_or_tuple
        key = self.project_key(key)
        self.check_key(key)
        if not self.allow_overwrite and key in self.data_dict.keys():
            raise ValueError(
                f"Tried to overwrite value at {key_as_dict_or_tuple} from {self.data_dict[key]} to {value}")
        self.data_dict[key] = value

    def lookup(self, key_as_dict_or_tuple):
        if isinstance(key_as_dict_or_tuple, dict):
            key = self.key_var_value_dict_to_key_tuple(key_as_dict_or_tuple)
        else:
            assert isinstance(
                key_as_dict_or_tuple, tuple), f'Found type {type(key_as_dict_or_tuple)} but must be dict or tuple.'
            key = key_as_dict_or_tuple
        key = self.project_key(key)
        self.check_key(key)
        return self.data_dict[key]


def export_states(model_path, state_export_path, quiet=True):
    quiet
    try:
        # Define the command and its arguments
        command = [
            "prism",
            model_path,
            "-exportstates",
            state_export_path
        ]
        # Run the command
        result = subprocess.run(command, check=True,
                                capture_output=True, text=True)

        # Print the output
        if not quiet:
            print("Command Output:\n", result.stdout)
        if len(result.stderr) > 0:
            print("Command Error:\n", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the command: {e}")
    except FileNotFoundError:
        print("The 'prism' command was not found. Please ensure it is installed and in your PATH.")


def state_to_conjunction(state_cipher, state, prime_marks=False):
    ''' Eventually would be nice to be able to project out parts of the state space. 
        Or to ignore nop componenet updates. 
        Also would be nice to enforce a canonical order on the vars. '''
    var_dict = state_cipher.forward_lookup(state)
    conj = ""
    for k, v in var_dict.items():
        prime = "'" if prime_marks else ""
        conj = conj + f" & ({k}{prime}={v})"
    conj = conj.removeprefix(" & ")
    return conj

### Summaries ###


def save_explicit_summaries(sta_file_path, tra_file_path, error_pred, representative_error_valuation, scenario_var_name='scenario', export_directory=None, export_filename_stem=None, rounding_decimals=3):
    ''' sta_file_path and tra_file_path are for a single summary. Scenario should not appear as a variable, since the 
        file only contains one summary. If multiple summaries are needed, use parse_summaries function.
        error_pred : dict(str, int) -> bool is an error predicate. It cannot depend on the value of scenario_var_name
            (this might require you to rewrite your prism model so error can be detected the same way in each scenario.)
        representative_error_valuation needs to satisfy error_pred. We will make this state 0 of the explicit summary
        be the error state (all states that satisfy error_pred quotiented together) and this will be their error pred.
        the summaries and let it  
        0th state is error state (departure from previous). '''
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
        export_filename_stem = os.path.basename(sta_file_path).split('.'[0])
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
    system_state_valuation_tuples = []
    scenario_values = set()
    for s in original_cipher.states_set():
        valuation = original_cipher.forward_lookup(s)
        scenario_values.add(valuation[scenario_var_name])
        if not error_pred(valuation):
            valuation_tuple = tuple([valuation[var_name]
                                    for var_name in system_var_name_list])
            system_state_valuation_tuples.append(valuation_tuple)
    system_state_valuation_tuples = sorted(system_state_valuation_tuples)
    new_state_valuation_tuples = system_state_valuation_tuples.copy()
    new_state_valuation_tuples.append(representative_error_valuation_tuple)
    new_n = len(new_state_valuation_tuples)
    # Write the .sta file (do this here so we can build a new state cipher)
    sta_file_lines = [f"{string_of_tuple(system_var_name_list)}\n"]
    for s, valuation_tuple in enumerate(new_state_valuation_tuples):
        sta_file_lines.append(f"{s}:{string_of_tuple(valuation_tuple)}\n")
    with open(sta_export_path, 'w') as f:
        f.writelines(sta_file_lines)
    print(f"Wrote new state cipher to {sta_export_path}")
    new_cipher = cutil.StateCipher(sta_export_path)
    # Now for each scenario we need to make a confusion matrix. I'll make C first then cut it into A and b.
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
            source_valuation = original_cipher.forward_lookup(old_source_s)
            dest_valuation = original_cipher.forward_lookup(old_dest_s)
            assert source_valuation[scenario_var_name] == dest_valuation[
                scenario_var_name], ".tra file contains a transition between scenarios"
            scenario_index = scenario_values.index(
                source_valuation[scenario_var_name])
            if error_pred(source_valuation):
                # We will add transitions from error states later
                continue
            new_source_s = new_cipher.backward_lookup(source_valuation)
            if error_pred(dest_valuation):
                # Add prob to the error state, which is 0
                C_list[scenario_index][new_source_s, -1] += prob
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
    A_list = [C[1:, 1:].copy() for C in C_list]
    b_list = [C[0, 1:].copy() for C in C_list]
    # Now we need to save all of these matrices. I could save them as numpy arrays, but instead I will save as pickle.
    save_dict = {}
    save_dict["states_header"] = np.array(system_var_name_list)
    save_dict["states_list"] = np.array(new_state_valuation_tuples)
    for scenario, C, A, b in zip(scenario_values, C_list, A_list, b_list):
        save_dict[f"C_{scenario}"] = C
        save_dict[f"A_{scenario}"] = A
        save_dict[f"b_{scenario}"] = b
    with open(tra_export_path, 'rb') as f:
        np.savez_compressed(f, **save_dict)


### Below this line is things that have not been incorporated anywhere ###


class PrismCommandSimple():
    # I haven't incorporated this anywhere, but this will be useful for
    # eliminating nop assingments.
    # This is going to represent a command.
    # A simple command can only have = in guards and assignments.
    # Also, rhs of updates must be literals.
    # update_pairs is multilevel.
    # update_pairs : list(probability x (var_name x var_value))
    def __init__(self, guard_pairs, update_pairs, action_label=""):
        self.guard_pairs = guard_pairs
        self.update_pairs = update_pairs
        self.action_label = action_label

    def to_string(self):
        guard = ""
        for var_name, value in self.guard_pairs:
            guard = f"{guard} & ({var_name}={value})"
        guard.removeprefix(" & ")

        update_terms = []
        for p, pair_list in self.update_pairs:
            update_term = ""
            for var_name, value in pair_list:
                update_term = f"{update_term} & ({var_name}'={value})"
            update_term = update_term.removeprefix(" & ")
            update_term = f"{p}: {update_term}"
            update_terms.append(update_term)
        rhs = ""
        for update_term in update_terms:
            rhs = f"{rhs} + {update_term}"
        rhs.removeprefix(" + ")
        return f"[{self.action_label}] {guard} -> {rhs};"


def create_prism_command_simple(line):
    lhs, rhs = [e.strip().removesuffix(";").strip() for e in line.split("->")]
    action_label, guard = [e.strip().removeprefix("[").strip()
                           for e in lhs.split("]")]
    guard_terms = [e.strip().strip("() ") for e in guard.split("&")]
    raise NotImplementedError
    # Each guard term now looks like "varname = statevalue"
    # Could assert that there are not any other values in here.


def project_commands(commands, variable_value_equalities):
    ''' For all of these commands, project out reference of each variable
        appearing in variable. This is going'''
    raise NotImplementedError
    new_commands = []
    for command in commands:
        pass
        # First we need to parse the command
