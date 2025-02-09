# Analysis for sequences of scenarios.

import numpy as np
from explicit_summaries import encode_assertion, encode_distribution
from analysis import Polyhedron


def compute_error_probability(explicit_summaries_path, scenario_sequence, initial_distribution=None):
    ''' 
        # This seems like it should belong in the analysis section.
        Compute error probability for a linear sequence of scenarios, either concretely or symbolically.
        Inputs:
            explicit_scenarios_path: Path to .npz file saved by save_explicit_summaries function.
            scenario_sequence: list(int). Sequence of scenarios (each expressed as the value of the PRISM variable used
                to define scenarios.)
            initial_distribution: Either a numpy array of shape (n-1,) that represents a probability distribution over
                the non-error states present in the summaries, or None. If None, we will return an array of shape (n-1,)
                such that the dot product of that array with any distribution over the non-error states will yield the
                probability of error.
    '''
    with open(explicit_summaries_path, 'rb') as f:
        summaries = dict(np.load(f))
    # Now need to do a fold that is matrix multiplication.
    combined_C = np.identity(len(summaries['states_list']), dtype=np.float64)
    for i in scenario_sequence:
        np.matmul(combined_C, summaries[f'C_{i}'], out=combined_C)
    # combined_C is now the right-stochastic matrix for the entire sequence.
    combined_b = combined_C[:-1, -1]
    if initial_distribution is None:
        return combined_b
    else:
        return np.dot(initial_distribution, combined_b)


def compute_max_error_probability(explicit_summaries_path, scenario_sequence, predicate_list, offset_list):
    # First get the combined b
    combined_b = compute_error_probability(
        explicit_summaries_path, scenario_sequence)
    # Next, encode the precondition as a Polyhedron.
    coefficients_matrix, offsets_vector = encode_assertion(
        explicit_summaries_path, predicate_list, offset_list)
    precondition = Polyhedron(coefficients_matrix, offsets_vector)
    return precondition.strongest_eps(combined_b)
