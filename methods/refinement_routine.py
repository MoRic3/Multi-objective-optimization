#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 09:53:49 2024

@author: moritz
"""

import copy as cp

from adaptive_refinement import *
from OBBT import *
from uniform_refinement import *

def refinement_routine(call_model, solution, rel_errors, info, u, options):
    """
    routine for refining a box-based relaxation by either applying OBBT w.r.t.
    the search zone constraint 'u' or by further partitioning the boxes

    Parameters
    ----------
    call_model : function
        returning a pyomo model of the problem to be solved.
    solution : dict
        having the variable names as keys and the corresponding optimal values
        as values.
    rel_errors : dict
        having the constraint names as keys and the corresponding constraint
        satisfaction errors as values.
    info : dict
        containing all information for setting up the current piecewise linear
        relaxation of the problem of interest.
    u : ndarray
        representing the image space vector determining the search zone.
    options : structure
        containing all optional settings for the algorithm.

    Returns
    -------
    info : dict
        containing all information for setting up the refined piecewise linear
        relaxation of the problem of interest.
    tighten_time : float
        representing the time needed for solving the OBBT problems.
    tighten_counter : int
        representing the number of solved OBBT problems.

    """
    
    
    # catch options
    # if adaptive refinement should be applied
    try:
        adaptive_refinement = options.adaptive_refinement
    except:
        adaptive_refinement = False
    
    # if and when bound tightening should be applied
    try:
        bound_tightening = options.bound_tightening
    except:
        bound_tightening = 1e20
        
    # save old relaxation information
    old_info = cp.deepcopy(info)
    tighten_time = 0
    tighten_counter = 0
    
    # check if it is time for bound tightening
    if info['BT counter'] >= bound_tightening:
        print('apply bound tightening')
        info, tighten_time, tighten_counter = OBBT(
            call_model,
            rel_errors,
            solution,
            u,
            info,
            options)
        
        # reset bound tightening counter
        info['BT counter'] = 0
    
    else:
        print('apply domain partitioning:', rel_errors['max_error'])
        
        # check which partitioning routine should be applied
        if adaptive_refinement:
            info = adaptive_refinement_procedure(
                info,
                solution,
                rel_errors,
                options)
            
        else:
            info = uniform_refinement_procedure(info, rel_errors, options)
    
    return info, tighten_time, tighten_counter