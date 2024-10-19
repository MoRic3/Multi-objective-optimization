#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 10:03:00 2024

@author: moritz
"""

from pyomo.environ import *
import numpy as np
import sys

from rounding_routines import *

import logging
logging.getLogger('pyomo.core').setLevel(logging.ERROR)

def restricted_weighted_sum_feas(model, m, alpha, u, options):
    """
    routine for solving the weighted sum problem determined by the weight
    vector 'alpha' restricted by objective cut-offs determined by the local
    upper bound 'u' to feasibility

    Parameters
    ----------
    model : pyomo model
        representing the problem instance of interest.
    m : int
        representing the number of objective functions.
    alpha : ndarray
        contains specific weight for each of the objective functions.
    u : ndarray
        representing the restrictions on the objective function components.
    options : structure
        containing all optional settings for the algorithm.

    Returns
    -------
    objective_vector : ndarray
        representing the values of the objective function components.
    solution : dict
        with variable names as keys and respective values as values.
    sol_time : float
        representing the solution time of the problem.

    """
    
    try:
        solver = options.nlp_solver
    except:
        solver ='scip'

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
    if solver=='scip':
        opt.options['limits/solutions'] = 1
        
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

    return objective_vector, solution, sol_time
