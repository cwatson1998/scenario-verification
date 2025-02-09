# This is a different AST than the one used by the compiler for PRISM. The only salient difference is that this one
# will allow iter (with k). Also, this one does not have a frontend and is also not executable.
# We are going to write these by hand
# The "check" functionality is willing to apply the contraction rule.
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import z3
import sympy


# DEFAULT_TOLERANCE = 0.0001
DEFAULT_TOLERANCE = 0


### Analysis for programs ###

def coefficients_to_z3_expression(coeffs, x):
    '''
        coeffs is a list or 1d ndarray of coefficients
        x is a list of z3.Real decision variables.
        Note: This ignores coefficients that == 0, which depends of floating point comparions.
    '''
    nonzero_pairs = []
    for c, xi in zip(coeffs, x):
        c = float(c)
        if c != 0:
            nonzero_pairs.append((c, xi))
    if len(nonzero_pairs) == 0:
        return 0
    else:
        acc = nonzero_pairs[0][0] * nonzero_pairs[0][1]
        for c, xi in nonzero_pairs[1:]:
            acc = acc + (c * xi)
        return acc


class Polyhedron():
    ''' Class defining an assertion as an intersection of affine constraints. '''

    def __init__(self, coefficients_matrix, offsets, label=None):
        ''' A row vector x is in the polyhedron iff coefficients_matrix @ x.T < offsets where < is elementwise.
            That is, coefficients_matrix[i] is coefficients on the components of x such that the sum has 
            to be less than the offsets[i].

            When using these as assertions, we can choose not to include the inequalities that assure
            we are dealing with a distribution, because that is an invariant that is maintained elsewhere.    
        '''
        if not (len(coefficients_matrix) == 0 and len(offsets) == 0):
            m, _ = coefficients_matrix.shape
            assert (
                m,) == offsets.shape, f"Found {m} so expected that many offsets but offsets had shape {offsets.shape}"
        self.coefficients_matrix = coefficients_matrix
        self.offsets = offsets
        self.label = label

    def contains_vector(self, x, tolerance=DEFAULT_TOLERANCE):
        return ((self.coefficients_matrix @ x.T) <= self.offsets + tolerance).all()

    def z3_constraints(self, x):
        ''' 
            x is a list of z3.Real decision variables.
        '''
        if len(self.offsets) == 0:
            # This allows self.coefficients_matrix to be [[]]
            return []
        constraints = []
        for coefficients, offset in zip(self.coefficients_matrix, self.offsets):
            offset = float(offset)
            expr = coefficients_to_z3_expression(coefficients, x)
            constraints.append(expr <= offset)
        return constraints

    def weakest_pre(self, A, b, eps=None, label="UNLABELED_WP"):
        '''
            A and b describe a summary of one of our scenarios.
        '''
        # Going to proceed individually by rows of self.coefficients_matrix.
        # Let the ith row be m[i] and the ith offset be d[i]
        # Turn (xA/(1-xb))m[i] <= d[i] into the form xm'[i] <= d[i].
        # (xA)m[i] <= d[i](1-xb)
        # (xA)m[i] <= d[i] - x(d[i] * b)
        # (xA)m[i] + x(d[i] * b) <= d[i]
        # x(Am[i]) + x(d[i] * b) <= d[i]
        # x(Am[i] + d[i] * b) <= d[i]
        # m'[i] = (Am[i] + d[i] * b)
        # Now I can stack the m'[i] to obtain the coeff matrix of the weakest pre.
        # Initialize M_prime with values that we will overwrite
        M_prime = np.ones_like(self.coefficients_matrix) * -9999
        for i, m_i in enumerate(self.coefficients_matrix):
            M_prime[i] = (A @ m_i) + (self.offsets[i] * b)
        # Now M_prime is strong enough to enforce Y. We just need to add eps.
        wp = Polyhedron(M_prime, self.offsets, label=label)
        if eps is not None:
            wp = wp.add_inequalities(b, float(eps), label=label)
        # print("Debug. Polyhedron.weakest_pre is about to return a polyhedron with")
        # print(wp.coefficients_matrix)
        # print(wp.offsets)
        return wp

    def strongest_eps(self, b, quiet=True):
        # Compute the strongest epsilon when this polyhedron is the precondition and b is the error prob vector.
        # Strongest means smallest.
        # Use Gurobi to maximize np.dot(x,b) | x \in self.
        with gp.Env() as env, gp.Model("strongest_eps", env=env) as m:
            m.setParam("OutputFlag", int(not quiet))
            # Create variables
            # This is n-1 variables, one for all of the system states.
            # The lb and ub ensure that they are between 0 and 1.
            # This is useful documentation https://docs.gurobi.com/projects/optimizer/en/current/reference/python/model.html#Model.addMVar
            x = m.addMVar(shape=len(b),
                          vtype=GRB.CONTINUOUS, name="x", lb=0, ub=1)
            # eps = m.addVar(lb=0, ub=1,
            #    vtype=GRB.CONTINUOUS, name='eps')
            error_mlexpr = (x @ b)

            m.setObjective(error_mlexpr, GRB.MAXIMIZE)
            # Constraint 1: Sum of x must be exactly 1 (n.b. x excludes err)
            m.addConstr(x.sum() == 1, name='pdist')
            # Now add the constraints from self
            m.addConstr(self.coefficients_matrix @ x <=
                        self.offsets, name="precondition")

            m.optimize()

            return m.ObjVal

    def strongest_post_pair(self, A, b, label="UNLABELED_SP"):
        ''' A and b describe a summary of one of our scenarios. 
            This returns a pair of:
                Y: a polyhedron representing the strongest post on the system states. 
                eps: a float representing the maximum epsilon.
        '''
        raise NotImplementedError("Not implemented.")
        # Even if we ignored b (assumed it was 0 vector) finding Y from X is a little bit hard when A is not
        # invertible. ChatGPT suggested code that projects down to to a lower dimension in this case.
        # Another option would be to first convert to V-representation and then work with that, but that might be
        # hard too.

    def add_inequalities(self, coefficients, offsets, label=None):
        # If offsets is a scalar, this can yield a np.int64 offset.
        coefficients = np.atleast_2d(coefficients)
        offsets = np.atleast_1d(offsets)
        if label is None:
            label = f"UNLABELED AUGMENTATION OF {self.label}"
        if len(self.offsets) == 0:
            new_coefficients = coefficients
            new_offsets = offsets
        else:
            new_coefficients = np.vstack(
                [self.coefficients_matrix, coefficients])
            new_offsets = np.concatenate([self.offsets, offsets])
        # print("Debug. Polyhedron.add_inequalities is about to return:")
        # print(new_coefficients)
        # print(new_offsets)
        return Polyhedron(new_coefficients, new_offsets, label=label)

    def intersection(self, other_polyhedron, label=None):
        if label is None:
            label = f"{self.label} AND {other_polyhedron.label}"
        return self.add_inequalities(other_polyhedron.coefficients_matrix, other_polyhedron.offsets, label=label)
        # if len(self.offsets) == 0:
        #     return Polyhedron(other_polyhedron.coefficients_matrix, other_polyhedron.offsets, label=label)
        # if len(other_polyhedron.offsets) == 0:
        #     return Polyhedron(self.coefficients_matrix, self.offsets, label=label)
        # # Just concatenate the constraints.
        # return Polyhedron(
        #     np.concatenate(self.coefficients_matrix, other_polyhedron.coefficients_matrix),
        #     np.concatenate(self.offsets, other_polyhedron.offsets),
        #     label=label
        # )

    # def contains_other_helper(self, other_polyhedron, tolerance=DEFAULT_TOLERANCE):
    #     if tolerance > 0:
    #         raise NotImplementedError(
    #             "Have not implemented nonzero tolerance.")
    #     # If there are no constraints, then this is the vacuous polyhedron.
    #     if len(self.offsets) == 0:
    #         return True
    #     # Now we know there is at least one constraint
    #     m, n = self.coefficients_matrix.shape
    #     # Make decision variables for each system state.
    #     x = [z3.Real(f"x_{i}") for i in range(n)]
    #     # Create a solver
    #     solver = z3.Solver()
    #     precondition_constraints = []
    #     for xi in x:
    #         precondition_constraints.append(xi >= 0)
    #     precondition_constraints.append(sum(x) == 1)
    #     precondition_constraints.extend(self.z3_constraints(x))
    #     precondition = z3.And(precondition_constraints)

    #     postcondition = z3.And(other_polyhedron.z3_constraints(x))
    #     solver.add(z3.Implies(precondition, postcondition))
    #     # If

    def contains_vector_z3(self, vector):
        # If there are no constraints, then this is the vacuous polyhedron.
        if len(self.offsets) == 0:
            return True
        # Now we know there is at least one constraint
        m, n = self.coefficients_matrix.shape
        # Make decision variables for each system state.
        x = [z3.Real(f"x_{i}") for i in range(n)]
        # Create a solver
        solver = z3.Solver()

        # Constrain x to be a probability distribution
        solver.add([xi >= 0 for xi in x])
        solver.add([sum(x) == 1])

        # Add the constraints defined by self
        self_constraints = self.z3_constraints(x)
        solver.add(self_constraints)

    def contains_other(self, other_polyhedron, tolerance=DEFAULT_TOLERANCE):
        if tolerance > 0:
            raise NotImplementedError(
                "Have not implemented nonzero tolerance.")
        # If there are no constraints, then this is the vacuous polyhedron.
        if len(self.offsets) == 0:
            return True

        # Now we know there is at least one constraint
        m, n = self.coefficients_matrix.shape
        # Make decision variables for each system state.
        x = [z3.Real(f"x_{i}") for i in range(n)]
        # Create a solver
        solver = z3.Solver()

        # Constrain x to be a probability distribution
        solver.add([xi >= 0 for xi in x])
        solver.add([sum(x) == 1])

        # Add the constraints defined by the other polyhedron
        solver.add(other_polyhedron.z3_constraints(x))

        # Add the negation of the self constraints
        solver.add(z3.Not(z3.And(self.z3_constraints(x))))

        # Check that the model is not satisfiable.
        if solver.check() != z3.sat:
            return True
        else:
            print(
                f"Z3 says that {self.label} fails to contain {other_polyhedron.label}. The model was:")
            print(solver.model())
            print(
                f"That means we think that this vector is in {other_polyhedron.label} and but is not in {self.label}")
            return False

    def is_empty(self):
        ''' We use Z3 for this, but we could also have used Farkas' Lemma and the Fourier-Motzkin algorithm. '''
        if len(self.offsets) == 0:
            return False
        # Now we know there is at least one constraint
        m, n = self.coefficients_matrix.shape
        # Make decision variables for each system state.
        x = [z3.Real(f"x_{i}") for i in range(n)]
        # Create a solver
        solver = z3.Solver()

        # Constrain x to be a probability distribution
        solver.add([xi >= 0 for xi in x])
        solver.add([sum(x) == 1])

        # Add the constraints defined by self
        solver.add(self.z3_constraints(x))

        # See if there is a solution
        return solver.check() != z3.sat

    def pretty_print(self):
        return self.label if self.label is not None else "UNLABELED_ASSERTION"


class DecoratedNode():
    def __init__(self, X, Y, eps, label=None):
        ''' eps is either a float or a sympy expression. If it is a sympy expression, there must be only
            one variable for the checks to work. 
        '''
        self.label = label
        self.X = X
        self.Y = Y
        self.eps = eps
        self.children = []

    def get_size(self):
        size = 1
        if self.children is not None:
            for n in self.children:
                size += n.get_size()
        return size

    def check_local(self, tolerance=DEFAULT_TOLERANCE):
        raise NotImplementedError("Should be implemented by child class.")

    def check(self, tolerance=DEFAULT_TOLERANCE):
        for i, c in enumerate(self.children):
            c_ok = c.check(tolerance=tolerance)
            print(f"debug: child {i} of {self.label} checked as {c_ok}")
            if not c.check(tolerance=tolerance):
                return False
        return self.check_local(tolerance=tolerance)

    def epsilon_leq(self, eps1, eps2):
        ''' Check that eps1 <= eps2. 
            Works for either floats or sympy expressions. '''
        ineq = eps1 <= eps2
        if isinstance(ineq, bool):
            return ineq
        elif isinstance(ineq, sympy.Basic):
            assert len(
                ineq.free_symbols) <= 1, "Right now, at most one symbol (introduced by Iter) is supported"
            # This is because sympy can only reduce inequalities with at most one symbol.
            simplified = sympy.simplify(ineq)
            if isinstance(simplified, sympy.logic.boolalg.BooleanTrue):
                return True
            else:
                print(
                    f"When checking the inequality {ineq}, sympy reduced it to {simplified}, which is not valid, so the check failed.")
                return False
        else:
            raise NotImplementedError(
                f"epsilon comparison yielded a type {type(ineq)} which is not supported.")

    def preorder_traversal(self):
        # Return a list that is a preorder traversal from this node.
        traversal = [self]
        for c in self.children:
            traversal = traversal + c.preorder_traversal()
        assert len(traversal) == self.get_size()
        return traversal

    def child_index_to_preorder_offset(self, child_i):
        # Return the offset from the current node's position in the pre-order traversal
        # to the position of the child at child_i. We start indexing children at 0.
        if child_i > len(self.children):
            raise ValueError(
                f"Tried to find the preorder offset to the {child_i}th of a node with only {len(self.children)} children.")
        else:
            offset = 1
            for earlier_child in self.children[:child_i]:
                offset += earlier_child.get_size()
        return offset

    def set_weakest_assertions(self, new_Y):
        ''' Update self.Y to new_Y and adjust self.X and X and Y of all children to 
            be the weakest assertions that uphold new_Y. Does not modify any epsilons. '''
        raise NotImplementedError("Should be implemented by subclasses.")

    def set_non_atomic_epsilons(self):
        ''' Update the epsilons of the non-atomic commands to be as strong as possible.
            No-op for PAssign, because epsilon is considered a property of an atomic command. '''
        raise NotImplementedError("Should be implemented by subclasses.")

    def set_non_atomic_epsilons_and_weakest_assertions(self, new_Y):
        ''' Update all epsilons of the non-atomic commands to be as small as possible,
            then update all the assertions to be the weakest ones that enforce all the
            epsilons and the final postcondition new_Y. '''
        self.set_non_atomic_epsilons()
        self.set_weakest_assertions(new_Y)

    def pretty_print_stem(self, ego_idx, ego_indent_level):
        return "//" + ("  " * ego_indent_level) + str(ego_idx) + ": "

    def decorate_pretty_print(self, infix):
        return f"[{self.X.pretty_print()}] {infix} [{self.Y.pretty_print()}] [{self.eps}]"

    def pretty_print(self, ego_idx, ego_indent_level):
        ''' Return a tree, formatted as a list of lines that start with comments. '''
        raise NotImplementedError("Each subclass should implement this.")


class DecoratedPAssignNode(DecoratedNode):
    def __init__(self, X, Y, eps, A, b, label=None):
        ''' state_value_str is of the form <prism_state>=<prism_value>'''
        super().__init__(X, Y, eps, label=label)
        self.A = A
        self.b = b

    def check_local_z3(self, tolerance=DEFAULT_TOLERANCE, quiet=True):
        if tolerance > 0:
            raise NotImplementedError(
                "Have not implemented nonzero tolerance.")

        # Make decision variables for each system state.
        x = [z3.Real(f"x_{i}") for i in range(len(self.A))]
        # Create a solver
        solver = z3.Solver()

        # Constrain x to be a probability distribution
        solver.add([xi >= 0 for xi in x])
        solver.add([sum(x) == 1])

        # Add in the constraints defined by X (the precondition)
        solver.add(self.X.z3_constraints(x))

        negated_postcondition_list = []
        # 1.1. Get expression for error prob
        error_prob_expr = coefficients_to_z3_expression(self.b, x)

        # 1.2. Add error prob constraint to postcondition
        negated_postcondition_list.append(error_prob_expr > float(self.eps))

        # 2. Add Y constraints to postcondition (Y)

        # 2.1. Make a list of expressions for xprime
        x_after_A = [coefficients_to_z3_expression(col, x) for col in self.A.T]

        # 2.2. Build the (negation of) the postcondition
        for coefficients, offset in zip(self.Y.coefficients_matrix, self.Y.offsets):
            offset = float(offset)
            # Y says "coefficients . (x_after_A / (1-b.x)) <= offset"
            # Multiply both sides "coefficients . x_after_A <= offset(1- (b . x))"
            # scalar multiplication distributes "coefficients . x_after_A <= offset - (offset(b) . x))"
            # Add to both sides: "(coefficients . x_after_A) + (offset(b) . x) <= offset"
            coeffs_dot_x_after_A = coefficients_to_z3_expression(
                coefficients, x_after_A)
            offset_b_dot_x = coefficients_to_z3_expression(offset * self.b, x)
            negated_postcondition_list.append(
                coeffs_dot_x_after_A + offset_b_dot_x > offset)
        # 2.3 Build a disjunction of each negated postcondition.
        # (This is the entire ``negated postcondition'')
        negated_postcondition = z3.Or(negated_postcondition_list)
        # print("Debug, negated postcondition")
        # print(negated_postcondition)

        # 2.3 Add the negated postcondition.
        solver.add(negated_postcondition)

        # 2.4. Check that the model is not satisfiable.
        if not quiet:
            print(solver)
        if solver.check() == z3.sat:
            print(
                f"Passign node {self.label} failed the Z3-based check. The model was:")
            print(solver.model())
            return False
        return True

    def check_local(self, tolerance=DEFAULT_TOLERANCE):
        return self.check_local_z3(tolerance=tolerance)

    def weakest_pre(self, label="UNLABELED_WP"):
        '''
            Y is a postcondition expressed as a Polyhedron.
            eps is a local error probability.
            Returns the biggest polyhedron X that ensures {X}self.A,self.b{self.Y}{self.eps}.
            Right now, eps has to be a float (we don't have symbolic polyhedra.)
            Note that this ignores self.X. In fact, it should be the case that:
            self.check_local() == (self.weakest_pre() contains self.X)
            Checking containment of polyhedra can be done with e.g. simplex algorithm.
        '''
        wp = self.Y.weakest_pre(self.A, self.b, eps=self.eps, label=label)
        # print("debug, DecoratedPAssignNode is about to return wp with")
        # print(wp.coefficients_matrix)
        # print(wp.offsets)
        return wp

    def set_weakest_assertions(self, new_Y):
        print("Debug: PAssignNode called set_weakest assertions")
        self.Y = new_Y
        self.X = self.weakest_pre()

    def set_non_atomic_epsilons(self):
        ''' no-op since we consider epsilon to be a property of the atomic scenario. '''
        pass

    def pretty_print(self, ego_idx, ego_indent_level):
        return [self.pretty_print_stem(ego_idx, ego_indent_level) + self.decorate_pretty_print(f"{self.label if self.label is not None else 'UNLABELED_ATOMIC_SCENARIO'}")]


class DecoratedSeqNode(DecoratedNode):
    # In the future it might be nice to make this n-ary.
    def __init__(self, X, Y, eps, children, label=None):
        '''Another option would be to not require us to supply X, Y, eps (just copy from children)'''
        super().__init__(X, Y, eps, label=label)
        self.children = children
        assert len(self.children) == 2, "We only support binary seq"

    def check_local(self, tolerance=DEFAULT_TOLERANCE):
        assert len(self.children) == 2
        init_ok = self.children[0].X.contains_other(
            self.X, tolerance=tolerance)
        seq_ok = self.children[0].Y.contains_other(
            self.children[1].X, tolerance=tolerance)
        end_ok = self.Y.contains_other(
            self.children[-1].Y, tolerance=tolerance)
        # eps_ok = self.eps + tolerance >= 1 - \
        #     (1-self.children[0].eps)*(1-self.children[0].eps)
        eps_ok = self.epsilon_leq(
            1-(1-self.children[0].eps)*(1-self.children[0].eps), self.eps+tolerance)
        return init_ok and seq_ok and end_ok and eps_ok

    def set_weakest_assertions(self, new_Y):
        assert len(self.children) == 2
        self.Y = new_Y
        self.children[1].Y = new_Y
        self.children[1].set_weakest_assertions(new_Y)
        self.children[0].set_weakest_assertions(self.children[1].X)
        self.X = self.children[0].X

    def set_non_atomic_epsilons(self):
        alpha = 1
        for c in self.children:
            c.set_non_atomic_epsilons()
            alpha = alpha * (1-c.eps)
        self.eps = 1 - alpha

    def pretty_print(self, ego_idx, ego_indent_level):
        print_lines = [self.pretty_print_stem(
            ego_idx, ego_indent_level) + f"[{self.X.pretty_print()}] " + f"seq("]
        for child_i, child in enumerate(self.children):
            print_lines = print_lines + child.pretty_print(
                ego_idx + self.child_index_to_preorder_offset(child_i), ego_indent_level + 1)
        print_lines.append(self.pretty_print_stem(
            ego_idx, ego_indent_level) + f") [{self.Y.pretty_print()}] [{self.eps}]")
        return print_lines


class DecoratedChoiceNode(DecoratedNode):

    def __init__(self, X, Y, eps, children, label=None):
        '''Another option would be to not require us to supply X, Y, eps (just copy from children)'''
        super().__init__(X, Y, eps, label=label)
        self.children = children
        assert len(self.children) > 0
        assert len(self.children) > 0

    def check_local(self, tolerance=DEFAULT_TOLERANCE):
        # My precondition should contain all children's!!!
        # A precondition is a set.
        # The child set should contain the parent set. That way, anything that is ok for the parent is ok for the child.
        # This can be achieved by making the parent set the intersection of the child sets.

        for i, c in enumerate(self.children):
            print("i is " + str(i))
            print("c.X.contains_other(self.X, tolerance=tolerance) evals to ")
            print(c.X.contains_other(self.X, tolerance=tolerance))
            if not c.X.contains_other(self.X, tolerance=tolerance):
                print(
                    f"Choice precondition is weaker than  its {i}th child's")
                return False
            if not self.Y.contains_other(c.Y, tolerance=tolerance):
                print(
                    f"Choice postcondition is stronger than its {i}th child's")
                return False
            if not self.epsilon_leq(c.eps, self.eps):
                print(f"Choice error prob is stronger than its {i}th child's")
                return False
        return True

    def set_weakest_assertions(self, new_Y):
        print("Debug: ChoiceNode called set_weakest assertions")
        self.Y = new_Y
        for c in self.children:
            c.set_weakest_assertions(new_Y)
            self.X = self.X.intersection(c.X, label="CHOICE_WP")

    def set_non_atomic_epsilons(self):
        self.eps = 0
        for c in self.children:
            c.set_non_atomic_epsilons()
            self.eps = max(self.eps, c.eps)

    def pretty_print(self, ego_idx, ego_indent_level):
        print_lines = [self.pretty_print_stem(
            ego_idx, ego_indent_level) + f"choice"]
        for child_i, child in enumerate(self.children):
            print_lines = print_lines + child.pretty_print(
                ego_idx + self.child_index_to_preorder_offset(child_i), ego_indent_level + 1)
        return print_lines


class DecoratedIterNode(DecoratedNode):

    def __init__(self, X, Y, eps, children, iter_symbol_str=None, label=None):
        ''' {X} (children[0])^iter_symbol {Y}{eps} 
            As a convenience, if eps is None and iter_symbol_str is a str, we will set eps based on children[0].eps
        '''
        super().__init__(X, Y, eps, label=label)
        self.children = children
        if len(self.children) != 1:
            raise ValueError("Iter must have exactly one child.")
        self.iter_symbol = None  # placeholder
        if isinstance(eps, sympy.Basic):
            assert len(
                eps.free_symbols) <= 1, "At most one free symbol is allowed."
            if len(eps.free_symbols) == 1:
                assert iter_symbol_str is None, "eps expression already contained a symbol"
                self.iter_symbol = eps.free_symbols[0]
                assert self.iter_symbol.is_nonnegative
                assert self.iter_symbol.is_integer

        if self.iter_symbol is None:
            self.iter_symbol = sympy.Symbol(
                name=iter_symbol_str, integer=True, nonnegative=True)

    def check_local(self, tolerance=DEFAULT_TOLERANCE):
        c = self.children[0]
        if not c.X.contains_other(self.X, tolerance=tolerance):
            print("Iter precondition is weaker than its child's")
            return False
        if not self.Y.contains_other(c.Y, tolerance=tolerance):
            print("Iter postcondition is stronger than its child's")
            return False
        if not self.epsilon_leq(c.eps**self.iter_symbol, self.eps):
            print("Iter error prob is stronger than its child's")
            return False
        if not self.X.contains_other(self.Y, tolerance=tolerance):
            print(
                "Iter postcondition does not imply the precondition (i.e., not recurrent)")
            return False
        return True

    def set_weakest_assertions(self, new_Y):
        raise NotImplementedError(
            "Set weakest assertions not implemented for Iter.")

    def set_non_atomic_epsilons(self):
        self.children[0].set_non_atomic_epsilons()
        c_eps = self.children[0].eps
        self.eps = (self.children[0].eps) ** self.iter_symbol
        self.eps = sympy.simplify(self.eps)

    def pretty_print(self, ego_idx, ego_indent_level):
        print_lines = [self.pretty_print_stem(
            ego_idx, ego_indent_level) + f"[{self.X.pretty_print()}] " + f"{self.iter_symbol} iterations of ("]
        for child_i, child in enumerate(self.children):
            print_lines = print_lines + child.pretty_print(
                ego_idx + self.child_index_to_preorder_offset(child_i), ego_indent_level + 1)
        print_lines.append(self.pretty_print_stem(
            ego_idx, ego_indent_level) + f") [{self.Y.pretty_print()}] [{self.eps}]")
        return print_lines
