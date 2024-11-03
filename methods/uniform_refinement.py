#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 10:17:49 2024

@author: moritz
"""

import copy as cp
import numpy as np
import sys

def uniform_refinement_procedure(info, rel_errors, options):
    """
    routine for uniform refinement of current relaxation, that is performing
    a longest edge bisection of each box belonging to a partition of a variable
    domain box of a constraint which is violated to heavily

    Parameters
    ----------
    info : dict
        containing all information for setting up the current piecewise linear
        relaxation of the problem of interest.
    rel_errors : dict
        having the constraint/objective names as keys and the corresponding
        constraint/objective violation errors as values.
    options : structure
        containing all optional settings for the algorithm.

    Returns
    -------
    info : dict
        containing all information for setting up the refined piecewise linear
        relaxation of the problem of interest.

    """
    
    # catch constraint violation tolerance
    try:
        cons_vio_tol = options.constraint_tolerance
    except:
        cons_vio_tol = 1e-3
        
    # determine constraints and objectives which are violated too heavily
    bad_cons = [c for c in list(rel_errors.keys()) if rel_errors[c] > cons_vio_tol]
    bad_cons.remove('max_error')
    
    for c in bad_cons:
        # catch boxes belonging to partition for that constraint
        boxes = [b for b in list(info[c].keys()) if 'box' in b]
        
        for b in boxes:
            # catch variable names relevant for that constraint
            vars = list(info[c][b].keys())
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
            
            # check for discrete variables that should not be bisected anymore
            delete_box = False
            vars_check = cp.deepcopy(vars)
            for v in vars_check:
                if 'discrete' in info['bounds'][v]:
                    if np.ceil(info[c][b][v][0]) == np.floor(info[c][b][v][1]):
                        vars.remove(v)
                    elif np.ceil(info[c][b][v][0]) > np.floor(info[c][b][v][1]):
                        delete_box = True
                        break
            
            if delete_box:
                del info[c][b]
                continue
            
            # find longest edge of box
            max_var = None
            max_len = 0
            for v in vars:
                if info[c][b][v][1] - info[c][b][v][0] > max_len:
                    max_len = info[c][b][v][1] - info[c][b][v][0]
                    max_var = v
            
            # make sure we have max_var
            if type(max_var) == str:
                # delete old weights and stuff
                try:
                    del info[c][b]['weight']
                except:
                    None
                try:
                    del info[c][b]['underest_error']
                except:
                    None
                try:
                    del info[c][b]['overest_error']
                except:
                    None
                
                # build new boxes
                info[c][b+'0'] = cp.deepcopy(info[c][b])
                if 'discrete' in info['bounds'][max_var]:
                    info[c][b+'0'][max_var][1] = np.floor(info[c][b][max_var][0] + max_len/2)
                    
                else:
                    info[c][b+'0'][max_var][1] = info[c][b][max_var][0] + max_len/2
                
                info[c][b+'1'] = cp.deepcopy(info[c][b])
                if 'discrete' in info['bounds'][max_var]:
                    info[c][b+'1'][max_var][0] = np.ceil(info[c][b][max_var][0] + max_len/2)
                
                else:
                    info[c][b+'1'][max_var][0] = info[c][b][max_var][0] + max_len/2
                
                del info[c][b]
            
    
    return info
                