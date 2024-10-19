#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 13:57:54 2024

@author: moritz
"""

import copy as cp
import numpy as np
import sys

def adaptive_refinement_procedure(info, solution, rel_errors, options):
    """
    routine for adaptive refinement of current relaxation, that is
    performing a longest edge bisection of the active box
    foundational pseudo code can be found in
    
    Eichfelder, G. and Link, M. and Volkwein, S. and Warnow, L.
    An adaptive relaxation-refinement scheme for multi-objective mixed-integer
    nonconvex opimization.
    2024.
    
    Algorithm 4.

    Parameters
    ----------
    info : dict
        containing all information for setting up a piecewise linear
        relaxation of the problem of interest.
    solution : dict
        having the variable names as keys and the corresponding optimal
        values as values.
    rel_errors : dict
        having the constraint names as keys and the corresponding constraint
        satisfaction errors as values.
    options : structure
        containing all optional settings for the algorithm.

    Returns
    -------
    info : dict
        containing all information for setting up the refined piecewise
        linear relaxation of the problem of interest.

    """
    
    # catch constraint violation tolerance
    try:
        cons_vio_tol = options.constraint_tolerance
    except:
        cons_vio_tol = 1e-3
    
    # determine constraints and objectives which are violated too heavily
    bad_cons = [c for c in list(rel_errors.keys()) if rel_errors[c] > cons_vio_tol]
    try:
        bad_cons.remove('max_error')
    except:
        None
    
    for c in bad_cons:
        # catch boxes belonging to partition for that constraint
        boxes = [b for b in list(info[c].keys()) if 'box' in b]
        
        dummy_b = boxes[0]

        # catch variable names relevant for that constraint
        vars = list(info[c][dummy_b].keys())
        try:
            vars.remove('weight')
        except:
            None
        try:
            vars.remove('underest_error')
        except:
            None
        try:
            vars.remove('overest_error')
        except:
            None
            
        
        # find active box
        active_box = None
        act_bin = [i for i in list(solution.keys()) if (c in i and solution[i]>= 0.9)][0]
        act_ind = act_bin[act_bin.index('[')+1:act_bin.index(']')]
        
        active = True
            
        try:
            b = boxes[int(act_ind)]
        except:
            active = False
        
        # check if chosen box is truely active
        if active:
            for v in vars:
                if not(info[c][b][v][0] - 1e-5 <= solution[v] and solution[v] <= info[c][b][v][1] + 1e-5):
                    active = False
                    break
            if active:
                active_box = b

        if type(active_box) == str:
            
            # check for discrete variables that should not be bisected anymore
            for v in vars:
                if 'discrete' in info['bounds'][v]:
                    if np.ceil(info[c][active_box][v][0]) == np.floor(info[c][active_box][v][1]):
                        vars.remove(v)
            
            try:
                del info[c][active_box]['weight']
            except:
                None
            try:
                del info[c][active_box]['underest_error']
            except:
                None
            try:
                del info[c][active_box]['overest_error']
            except:
                None
            
            # find max var
            max_var = None
            max_len = 0
            for v in vars:
                if info[c][active_box][v][1] - info[c][active_box][v][0] > max_len:
                    max_len = info[c][active_box][v][1] - info[c][active_box][v][0]
                    max_var = v
            
            if type(max_var) == str:
                
                if 'discrete' in info['bounds'][max_var]:
                    # bisection for discrete vars
                    info[c][active_box+'0'] = cp.deepcopy(info[c][active_box])
                    info[c][active_box+'0'][max_var][1] = np.floor(
                        info[c][active_box][max_var][0] + max_len/2)
                    
                    info[c][active_box+'1'] = cp.deepcopy(info[c][active_box])
                    info[c][active_box+'1'][max_var][0] = np.ceil(
                        info[c][active_box][max_var][0] + max_len/2)
                
                else:
                    # bisection for continuous vars
                    info[c][active_box+'0'] = cp.deepcopy(info[c][active_box])
                    info[c][active_box+'0'][max_var][1] = max_len/2 + \
                        info[c][active_box][max_var][0]
                        
                    info[c][active_box+'1'] = cp.deepcopy(info[c][active_box])
                    info[c][active_box+'1'][max_var][0] = max_len/2 + \
                        info[c][active_box][max_var][0]
                        
                del info[c][active_box]
            
            else:
                print('found no longest edge')
                sys.exit(1)
                
        else:
            print('found no active box')
            sys.exit(1)
            
    return info
