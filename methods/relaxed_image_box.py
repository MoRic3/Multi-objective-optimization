#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 12:14:20 2024

@author: moritz
"""

import numpy as np
import sys

from relax_model import *
from relax_model_maximization import *
from rounding_routines import *

def relaxed_image_box(call_model, m, info, options):
    """
    routine for computing a box containing the image set of the original
    problem. The computation is based on using piecewise linear
    relaxations of the problem

    Parameters
    ----------
    call_model : function
        returning a pyomo model of the problem of interest.
    m : int
        representing the number of objective functions, i.e., dimension of the
        image space.
    info : dict
        containing all information neccessary for setting up the current 
        piecewise linear relaxation of the problem of interest.
    options : structure
        containing all optional settings for the algorithm.

    Returns
    -------
    zl : ndarray
        representing the lower left corner of the image box.
    zu : ndarray
        representing the upper right corner of the image box.

    """
    
    # catch options
    try:
        solver = options.milp_solver
    except:
        solver = 'gurobi'
    
    # initialize the vectors zl and zu
    zl = np.zeros(m)
    zu = np.zeros(m)
    
    # offset factor to guarantee strict inclusion of image set
    factor = 0.02
    
    # compute ideal point
    for i in np.arange(0,m):
        model = call_model(i)
        model, info, box_counter = relax_model(model, call_model, info)
        
        opt = SolverFactory(solver)
        
        results = opt.solve(model, tee=False)
        
        if results.solver.termination_condition != TerminationCondition.optimal:
            print('problem with box computation: no lower bound on objective'+str(i))
            sys.exit(1)
            
        # catch optimal value
        for o in model.component_objects(Objective):
            if o.active:
                zl[i] = rounding_lower(value(o),10)
                
    # compute reversed ideal point
    for i in np.arange(0,m):
        model = call_model(i)
        model, info, box_counter = relax_model_maximization(model, call_model, info)
        
        # maximization
        for o in model.component_objects(Objective):
            if o.active:
                o.sense = maximize
                
        opt = SolverFactory(solver)
        
        results = opt.solve(model, tee=False)
        
        if results.solver.termination_condition != TerminationCondition.optimal:
            print('problem with box computation: no upper bound on objective'+str(i))
            sys.exit(1)
        
        # catch optimal value
        for o in model.component_objects(Objective):
            if o.active:
                zu[i] = rounding_upper(value(o),10)
    
    return zl, zu