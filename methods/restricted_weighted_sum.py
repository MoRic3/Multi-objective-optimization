#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 15:31:58 2024

@author: moritz
"""

from pyomo.environ import *
import numpy as np
import sys

from rounding_routines import *

import logging
logging.getLogger('pyomo.core').setLevel(logging.ERROR)

def restricted_weighted_sum(model, m, alpha, u, tol=False, solver='scip'):
    """

    routine for solving the restricted weighted sum problem determined by local
    upper bound u and weight vector alpha

    Parameters
    ----------
    model : pyomo model
        representing the problem to be solved.
    m : int
        representing the number of objective functions.
    alpha : array
        contains the specific weight for each of the objective functions.
    u : array
        representing the restrictions on the objective function components.
    tol : boolean/float, optional
        indicating if gap tolerance should be adapted. The default is False.
    solver : str, optional
        determining the solver to be used for solving the problem. The default
        is 'scip'.

    Returns
    -------
    objective_vector : array
        representing the optimal values of the objective function components.
    solution : dict
        with variable names as keys and respectives optimal values as values.

    """

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
    opt = SolverFactory(solver)
    if tol:
        if solver=='scip':
            opt.options['limits/gap'] = tol
        elif solver=='gurobi':
            opt.options['MIPGap'] = tol

    results = opt.solve(model, tee=False)

    sol_time = results.solver.time 
    
    # check for optimality
    if results.solver.termination_condition == TerminationCondition.infeasible:
        return None, None, sol_time

    # retrieve objective values
    objective_vector = np.zeros(m)
    for i in np.arange(0,m):
        for o in model.component_objects(Objective):
            if 'objective'+str(i) in o.name:
                objective_vector[i] = rounding_upper(value(o),6)
            elif 'weighted_objective' in o.name:
                objective_value = rounding_upper(value(o),6)

    # retrieve solution
    solution = {}
    for v in model.component_objects(Var):
        if v.is_indexed():
            for i in v.index_set():
                solution[v[i].name] = value(v[i])
        else:
            solution[v.name] = value(v)

    if results.solver.gap != 0.0:
        print('hello')
    return objective_vector, solution, sol_time
