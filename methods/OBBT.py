#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 10:32:30 2024

@author: moritz
"""

import copy as cp
import numpy as np

from tighten_bound import *
from update_bounds import *

def OBBT(call_model, rel_errors, solution, u, info, options):
    """
    routine for optimization-based bound tightening w.r.t. the objective
    constraints given by 'u'

    Parameters
    ----------
    call_model : function
        returning a pyomo model of the problem to be solved.
    rel_errors : dict
        having the constraint names as keys and the corresponding constraint
        satisfation errors as values.
    solution : dict
        having the variable names as keys and the corresponding optimal
        values as values.
    u : ndarray
        representing the image space vector determining the search zone.
    info : dict
        containing all information for setting up the current piecewise linear
        relaxation.
    options : structure
        containing all optional settings for the algorithm.

    Returns
    -------
    info : dict
        containing all information for setting up the tightened piecewise
        linear relaxation.
    tighten_time : float
        representing the time needed for solving the OBBT problems.
    counter : int
        representing the number of solved OBBT problems.

    """
    
    # catch options
    # decide share of variables to be tightened
    try:
        var_count_OBBT = options.var_count_OBBT
    except:
        var_count_OBBT = 2
    
    # determine order of variables+lower/upper to be tightened
    var_list = list(info['bounds'].keys())
    pos_vars = {}
    for v in var_list:
        if 'discrete' in info['bounds'][v]:
            if np.ceil(info['bounds'][v][0]) == np.floor(info['bounds'][v][1]):
                continue
        pos_vars[v+'_lower'] = np.abs(np.round(solution[v] - info['bounds'][v][0],10))
        pos_vars[v+'_upper'] = np.abs(np.round(solution[v] - info['bounds'][v][1],10))
    
    sorted_vars = dict(sorted(pos_vars.items(),
                              key=lambda x:x[1],
                              reverse=True)).keys()
    
    # tighten vars
    counter = 0
    
    # tightening time
    tighten_time = 0
    
    # save old relaxation information
    old_info = cp.deepcopy(info)
    
    for v_ind in sorted_vars:
        if pos_vars[v_ind] > 0:
            v = v_ind[:-6]
            ind = v_ind[-5:]
            
            new_bound, sol_time = tighten_bound(call_model,
                                      v,
                                      ind,
                                      u,
                                      old_info,
                                      solution,
                                      options)
            
            info = update_bounds(new_bound, v, ind, info)
            tighten_time += sol_time
            
            counter += 1
            if counter >= np.floor(var_count_OBBT * len(var_list)):
                break

    return info, tighten_time, counter  
            
            
            
            
            
