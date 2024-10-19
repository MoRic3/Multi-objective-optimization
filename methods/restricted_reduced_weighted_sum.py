#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 16:55:41 2024

@author: moritz
"""

from pyomo.environ import *

import numpy as np

from rounding_routines import *

def restricted_reduced_weighted_sum(call_model, m, alpha, solution, u, options):
    """
    routine for solving the reduced, i.e., fixed integer variables, weighted
    sum problem with objective restrictions determined by the local upper bound
    'u' and the weight vector 'alpha'

    Parameters
    ----------
    call_model : function
        returning a pyomo model of the problem to be solved.
    m : int
        representing the number of objective functions/dimension of the image
        space.
    alpha : ndarray
        contains the specific weight for each of the objective functions.
    solution : dict
        having the variable names as keys and the corresponding optimal values 
        of the relaxed problem as values.
    u : ndarray
        representing the image space vector determining the search zone.
    options : structure
        containing all optional settings for the algorithm.

    Returns
    -------
    objective_vector : ndarray
        representing the optimal values of the objective function components.
    solution : dict
        with variable names as keys and respective optimal values as values.
    sol_time : float
        representing the solution time of the problem.

    """
    
    # catch nlp solver
    try:
        solver = options.nlp_solver
    except:
        solver = 'scip'
    
    # decide if nlp should be solved to feasibility only
    try:
        feasibility_only = options.nlp_feasibility_only
    except:
        feasibility_only = False
    
    # set up model
    model = call_model(0)
    
    # fix integer variables
    for v in model.component_objects(Var):
        if v.is_indexed():
            for i in v.index_set():
                if v[i].domain == Integers or v[i].domain == Binary:
                    v[i].fix(np.round(solution[v[i].name]))
                
        else:
            if v.domain == Integers or v.domain == Binary:
                v.fix(np.round(solution[v.name]))
            
    # set up weighted objective function
    for i in np.arange(0,m):
        for o in model.component_objects(Objective):
            if 'objective'+str(i) in o.name:
                o.deactivate()
                
                if i == 0:
                    model.add_component('weighted_objective',
                                        Objective(expr = o.expr * alpha[i]))
                else:
                    for obj in model.component_objects(Objective):
                        if 'weighted_objective' == obj.name:
                            obj.expr += o.expr * alpha[i]
                
                model.add_component('upper_bound_for_'+str(i)+'-th_objective',
                                    Constraint(expr = o.expr - u[i] <= 0))
    
    # solve the model
    opt = SolverFactory(solver)
    if feasibility_only:
        if solver=='scip':
            opt.options['limits/solutions'] = 1
    
    results = opt.solve(model, tee=False)
    
    # catch solution time
    sol_time = results.solver.time
    
    # check for infeasibility
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
    
    
    
    
