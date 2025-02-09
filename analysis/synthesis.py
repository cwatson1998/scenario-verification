# THis file contains code to help us guess recurrent X.
import gurobipy as gp
from gurobipy import GRB
import numpy as np
from analysis import Polyhedron, DecoratedPAssignNode


def look_for_recurrences(A, b, eps_low=0, eps_high=1, step=0.05):
    # NOTE: This used to be named "find_recurrence"
    # This iterates through values of epsilon, explicitly checking if:
    # {WP((A,b), True, eps)}(A,b){WP((A,b), True, eps)}{eps}.
    # For a range of eps values. This puts a very strict structure on the X considered,
    # so there is no guarantee it will find a recurrence if one exists.
    findings = []
    eps = eps_low
    while eps <= eps_high:
        wp_eps = Polyhedron(np.atleast_2d(b), np.asarray(
            [eps]), label=f"wp((A,b),{eps})")
        scen = DecoratedPAssignNode(wp_eps, wp_eps, eps, A, b, label=f"scen")
        recurrent = scen.check()
        findings.append((eps, recurrent))
        if recurrent:

            print(f"wp((A,b),{eps}) is recurrent")
        else:
            print(f"wp((A,b),{eps}) is not recurrent")
        eps += step
    for e in findings:
        print(e)


# def look_for_recurrences(A_list, b_list, eps_low=0, eps_high=1, step=0.05):
#     '''
#         Assume we have a command of the form C = CHOICE_{0<=i<len(A_list)}(A_list[i],b_list[i]).
#         Want to check if X = AND_{0<=i<len(A_list)}(WP((A_i,b_i), True, eps)) satisfies
#         {X}C{X}{eps}.
#     '''
#     eps = eps_low

#     while eps <= eps_high:
#         wp_eps = Polyhedron(np.atleast_2d(b), np.asarray(
#             [eps]), label=f"wp((A,b),{eps})")
#         scen = DecoratedPAssignNode(wp_eps, wp_eps, eps, A, b, label=f"scen")
#         if scen.check():
#             print(f"wp((A,b),{eps}) is recurrent")
#         else:
#             print(f"wp((A,b),{eps}) is not recurrent")
#         eps += step


def compute_lowest_recurrent_eps(full_C, min_non_err=0.0001, sol_output_path=None, quiet=False):
    '''
        NOTE: This used to be called compute_lowest_eps
        This is not an SP computation. Instead it finds:
        min_X(eps | {X}C{eps}{X})
        It currently does not tell you what this X is, just eos and one witness x in this X.
        If we use the WP computation in analysis.py, WP(C, X, eps) will not in general be
        recurrent. TODO: Find a good way to extract the set X.

        full_C is an ndarry of shape (n,n) that represents the stochastic matrix of the command.
            Position n is assumed to correspond to the distinguished error state.
        min_non_err is a technical requirement to avoid division by zero. The one step
            probability of non-error must be at least min_non_err.
        Returns:
            best_eps
            witness distribution. In general, this may be the only distribution that satisfies the best
                epsilon. But if you want to find more generally, then you can use the tooling in analysis
                .py to compute WP given the epsilon we found here.
        TODO: Figure out what error gets thrown if we don't have at least min_non_err.
        TODO: Add version that has more bells and whistles, like nondeterministic alternation and requiring
         certain distributions to be in the set. I have I ideas for this in my personal OneNote.
    '''
    try:
        with gp.Env() as env, gp.Model("compute_best_eps", env=env) as m:
            # Create variables
            # This is n-1 variables, one for all of the system states.
            # The lb and ub ensure that they are between 0 and 1.
            # This is useful documentation https://docs.gurobi.com/projects/optimizer/en/current/reference/python/model.html#Model.addMVar
            x = m.addMVar(shape=len(full_C)-1,
                          vtype=GRB.CONTINUOUS, name="x", lb=0, ub=1)
            eps = m.addVar(lb=0, ub=1-min_non_err,
                           vtype=GRB.CONTINUOUS, name='eps')
            non_error_reciprocal = m.addVar(
                vtype=GRB.CONTINUOUS, name='non_error_reciprocal')

            error_mlexpr = (x @ full_C[:-1, -1])
            # non_error_lexpr = (x @ full_C[:-1,:-1]).sum()
            non_error_mlexpr = 1 - error_mlexpr

            m.setObjective(eps, GRB.MINIMIZE)

            # Constraint 1: Sum of x must be exactly 1 (n.b. x excludes err)
            m.addConstr(x.sum() == 1, name='pdist')
            # Constraint 2: one step err
            m.addConstr(error_mlexpr <= eps, name='one_step')
            # Constraint 3: Technical detail to obtain non_eps_reciprocal value
            m.addConstr(non_error_mlexpr * non_error_reciprocal ==
                        1, name='non_error_reciprocal_constr')
            # Constrain 4: Recurrent
            one_step_non_error_mqexpr = (
                x @ full_C[:-1, :-1]) * non_error_reciprocal
            second_step_error_mqexpr = one_step_non_error_mqexpr @ full_C[:-1, -1]
            # second_step_non_err_mqexpr = 1 - second_step_error_mqexpr
            m.addConstr(second_step_error_mqexpr <= eps, name='second_step')

            # Optimize model
            m.optimize()
            m.sync()
            if sol_output_path is not None:
                m.write(sol_output_path)

            if not quiet:
                print(x.X)

                print(f"Obj: {m.ObjVal:g}")
            info = {'witness': x.X}
            return m.ObjVal, info

    except gp.GurobiError as e:
        print(f"Error code {e.errno}: {e}")

    except AttributeError:
        print("Encountered an attribute error")
