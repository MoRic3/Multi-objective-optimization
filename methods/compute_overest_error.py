#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 16:31:32 2024

@author: moritz
"""

import sys

from pyomo.environ import *
from rounding_routines import *

def compute_overest_error(call_model, cons, var_list, info):
    """
    routine for computing the overestimation error of a linear function
    determined by the weights 'weight' w.r.t. a nonlinear function determined
    by cons

    Parameters
    ----------
    call_model : function
        returning a pyomo model of the problem to be solved.
    cons : pyomo constraint object
        representing the nonlinear constraint function for which the
        overestimation error should be calculated.
    var_list : list
        containing pyomo variable objects appearing in the constraint
        function of interest.
    info : dict
        containing all information of the current box of interest.

    Returns
    -------
    overest_error : float
        representing the overestimaton error of the linear function
        with respect to the objecive function of interest.

    """
    
    # catch weight
    weight = info['weight']
    
    # set up small model
    small_model = ConcreteModel()
    
    # set up dummy model
    dummy = call_model(0)
    
    # introduce relevant variables
    for v in var_list:
        for v_dummy in dummy.component_objects(Var):
            if v.name == v_dummy.name:
                dummy.del_component(v_dummy)
                small_model.add_component(v_dummy.name, v_dummy)
                break
            
    # initialize objective
    for c_dummy in dummy.component_objects(Constraint):
        if cons.name == c_dummy.name:
            dummy.del_component(c_dummy)
            small_model.objective = Objective(expr = c_dummy.body)
            break
    
    # substract linear function from objective
    for v in small_model.component_objects(Var):
        v.lb = min(info[v.name])
        v.ub = max(info[v.name])
        small_model.objective.expr += -weight[v.name] * v

    small_model.objective.expr += - weight['constant']

    # solve the model and catch optimal value
    opt = SolverFactory('scip')
    results = opt.solve(small_model, tee=False)
    
    try:
        overest_error = -small_model.objective()
        overest_error = rounding_upper(overest_error,5)
    
    except:
        print('not able to compute solution for overest error')
        sys.exit(1)
    
    return overest_error 
    
