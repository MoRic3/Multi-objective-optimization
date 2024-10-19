#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 12:26:56 2024

@author: moritz
"""

from pyomo.environ import * 

from rounding_routines import *

def compute_underest_error_objective(call_model, obj, var_list, info):
    """
    routine for computing the underestimation error of a linear function
    determined by the weights 'weight' w.r.t. an objective function
    determined by the object 'obj' appearing in the model

    Parameters
    ----------
    call_model : function
        returning a pyomo model of the problem to be solved.
    obj : pyomo objective object
        representing the objective for which the underestimation error
        should be calculated.
    var_list : list
        containing pyomo variable objects appearing in the objective
        function of interest.
    info : dict
        containing all information of the current box of interest.

    Returns
    -------
    underest_error : float
        representing the underestimation error of the linear function
        w.r.t. the objective function of interest.

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
    for o_dummy in dummy.component_objects(Objective):
        if obj.name == o_dummy.name:
            dummy.del_component(o_dummy)
            small_model.objective = Objective(expr = o_dummy.expr)
            break
    
    # substract linear function from objective
    for v in small_model.component_objects(Var):
        v.lb = min(info[v.name])
        v.ub = max(info[v.name])
        small_model.objective.expr += - weight[v.name] * v
    
    small_model.objective.expr += - weight['constant']
    
    small_model.objective.sense = maximize
    
    # solve the model and catch optimal value
    opt = SolverFactory('scip')
    results = opt.solve(small_model, tee=False)
    underest_error = small_model.objective()
    underest_error = rounding_upper(underest_error,5)
    
    return underest_error