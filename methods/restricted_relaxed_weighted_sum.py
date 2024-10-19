#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 14:27:42 2024

@author: moritz
"""

from pyomo.environ import *
import numpy as np

from rounding_routines import *

import logging
logging.getLogger('pyomo.core').setLevel(logging.ERROR)

def restricted_relaxed_weighted_sum(model, m, alpha, u, options):
    """
    routine for solving a piecewise linear relaxation of the weighted sum
    problem determined by the weight vector 'alpha' restricted by objective
    cut-offs determined by the local upper bound 'u'

    Parameters
    ----------
    model : pyomo model
        representing a piecewise linear relaxation of the problem to be solved.
    m : int
        representing the number of objective functions.
    alpha : ndarray
        contains specific weight for each of the objective functions.
    u : ndarray
        representing the restrictions on the objective function components.
    options : structure
        containing all optional settings of the algorithm.

    Returns
    -------
    objective_vector : ndarray
        representing the optimal values of the objective function components.
    solution : dict
        with variable names as keys and respective optimal values as values.
    relaxation_errors : dict
        having the constraint/objective names as keys and the corresponding
        constraint/objective satisfaction errors as values.
    sol_time : float
        representing the solution time of the problem.

    """

    # catch options
    try:
        milp_solver = options.milp_solver
    except:
        milp_solver = 'gurobi'

    try:
        relative_constraint_errors = options.relative_constraint_errors
    except:
        relative_constraint_errors = False

    # establish weighted objective function and upper bound constraints
    wobj = {}
    for i in np.arange(0,m):
        for o in model.component_objects(Objective):
            if 'objective'+str(i) in o.name:
                o.deactivate()

                if i == 0:
                    model.add_component('weighted_objective',
                                        Objective(expr = alpha[i] * o.expr))

                else:
                    for obj in model.component_objects(Objective):
                        if 'weighted_objective' in obj.name:
                            obj.expr += alpha[i] * o.expr

                model.add_component('upper_bound_for_'+str(i)+'-th_objective',
                                    Constraint(expr = o.expr - u[i] <= 0))

    # solve the model
    opt = SolverFactory(milp_solver)
    results = opt.solve(model, tee=False)#, options={'threads':1}, tee=False)

    # catch solution time
    sol_time = results.solver.time

    # check for optimality
    if results.solver.termination_condition == TerminationCondition.infeasible:
        return None, None, None, sol_time

    # retrieve objective values
    objective_vector = np.zeros(m)
    for i in np.arange(0,m):
        for o in model.component_objects(Objective):
            if 'objective'+str(i) in o.name:
                objective_vector[i] = rounding_lower(value(o),6)
            elif 'weighted_objective' in o.name:
                objective_value = rounding_lower(value(o),6)

    # retrieve solution
    solution = {}
    for v in model.component_objects(Var):
        if v.is_indexed():
            for i in v.index_set():
                solution[v[i].name] = value(v[i])
        else:
            solution[v.name] = value(v)

    # determine relaxation_errors
    relaxation_errors = {}
    max_error = 0
    if relative_constraint_errors:
        for c in model.component_objects(Constraint):
            if c.body.polynomial_degree() != 1:
                if not 'objective' in c.name:
                    if not 'estimation' in c.name and not 'active' in c.name:
                        if c.lb == c.ub:
                            cons_rel_error = np.abs(c.ub - value(c))/max(np.abs(c.ub),1)
                            relaxation_errors[c.name] = cons_rel_error
                            max_error = max(max_error, cons_rel_error)
                        elif c.lb != None:
                            cons_rel_error = max(c.lb - value(c),0)/max(np.abs(c.lb),1)
                            relaxation_errors[c.name] = cons_rel_error
                            max_error = max(max_error, cons_rel_error)
                        elif c.ub != None:
                            cons_rel_error = max(value(c) - c.ub,0)/max(np.abs(c.ub),1)
                            relaxation_errors[c.name] = cons_rel_error
                            max_error = max(max_error, cons_rel_error)
                else:
                    if not 'estimation' in c.name and not 'active' in c.name:
                        for obj in model.component_objects(Objective):
                            if c.name in obj.name and 'estimation' in obj.name:
                                obj_rel_error = np.abs(value(c) - value(obj))/max(np.abs(value(c)),1)
                                relaxation_errors[c.name] = obj_rel_error
                                max_error = max(max_error, obj_rel_error)

    else:
        for c in model.component_objects(Constraint):
            if c.body.polynomial_degree() != 1:
                if not 'objective' in c.name:
                    if not 'estimation' in c.name and not 'active' in c.name:
                        if c.lb == c.ub:
                            cons_error = np.abs(c.ub - value(c))
                            relaxation_errors[c.name] = cons_error
                            max_error = max(max_error, cons_error)
                        elif c.lb != None:
                            cons_error = max(c.lb - value(c),0)
                            relaxation_errors[c.name] = cons_error
                            max_error = max(max_error, cons_error)
                        elif c.ub != None:
                            cons_error = max(value(c) - c.ub,0)
                            relaxation_errors[c.name] = cons_error
                            max_error = max(max_error, cons_error)
                else:
                    if not 'estimation' in c.name and not 'active' in c.name:
                        for obj in model.component_objects(Objective):
                            if c.name in obj.name and 'estimation' in obj.name:
                                obj_error = np.abs(value(c) - value(obj))
                                relaxation_errors[c.name] = obj_error
                                max_error = max(max_error, obj_error)


    relaxation_errors['max_error'] = max_error
    return objective_vector, solution, relaxation_errors, sol_time
