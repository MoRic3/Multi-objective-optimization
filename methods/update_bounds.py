#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 11:27:26 2024

@author: moritz
"""

import numpy as np


def update_bounds(new_bound, v, ind, info):
    """
    routine for updating the lower/upper -- indicated by 'ind' -- bound
    of variable 'v' in the relaxation information collection 'info'

    Parameters
    ----------
    new_bound : float
        representing the possibly tighter bound.
    v : str
        representing the name of the variable in question.
    ind : str
        indicating if lower or upper bound was tightened.
    info : dict
        containing all information for setting up the current piecewise linear 
        relaxation of the problem of interest.

    Returns
    -------
    info : dict
        containing all information for setting up the tightened piecewise
        linear relaxation of the problem of interest.

    """
    
    # round bound to integer if it belongs to an integer variable
    if 'discrete' in info['bounds'][v]:
        np.round(new_bound)

    # check if it new bound is in interval
    if info['bounds'][v][0] -1e-2 > new_bound or new_bound > info['bounds'][v][1] + 1e-2:
        print('something went wrong with bound computation -- ignore it')
        return info

    # update_global bounds
    check = False
    if ind == 'lower':
        if info['bounds'][v][0] < new_bound:
            info['bounds'][v][0] = new_bound
            check = True
    elif ind == 'upper':
        if info['bounds'][v][1] > new_bound:
            info['bounds'][v][1] = new_bound
            check = True

    if check:
        print('found new bound for:',v)
        # update constraint boxes
        for c in list(info.keys()):
            if not 'bounds' in c and not 'BT counter' in c:
                boxes = [b for b in info[c].keys() if 'box' in b]
                for b in boxes:
                    if v in list(info[c][b].keys()):
                        
                        # check if box info should be updated
                        if ind == 'lower':
                            if info[c][b][v][0] < new_bound:
                                
                                # check if box can be deleted
                                if info[c][b][v][1] < new_bound:
                                    del info[c][b]
                                    continue
                                
                                else:
                                    info[c][b][v][0] = new_bound
                                    
                                    # delete former box information
                                    try:
                                        del info[c][b]['weight']
                                    except:
                                        None
                                    try:
                                        del info[c][b]['overest_error']
                                    except:
                                        None
                                    try:
                                        del info[c][b]['underest_error']
                                    except:
                                        None

                                    # check if box is doubled
                                    current_boxes = [b for b in info[c].keys() if 'box' in b]
                                    for box in current_boxes:
                                        if box != b:
                                            same = True
                                            for var in list(info[c][b].keys()):
                                                if not info[c][box][var][0] == info[c][b][var][0]:
                                                    same = False
                                                    
                                                if not info[c][box][var][1] == info[c][b][var][1]:
                                                    same = False
                                                
                                            if same:
                                                print('found double box --> delete it')
                                                del info[c][b]
                                                break
                        
                        elif ind == 'upper':
                            if info[c][b][v][1] > new_bound:
                                
                                # check if box can be deleted
                                if info[c][b][v][0] > new_bound:
                                    del info[c][b]
                                    continue
                                
                                else:
                                    info[c][b][v][1] = new_bound
                                    
                                    # delete former box information
                                    try:
                                        del info[c][b]['weight']
                                    except:
                                        None
                                    try:
                                        del info[c][b]['overest_error']
                                    except:
                                        None
                                    try:
                                        del info[c][b]['underest_error']
                                    except:
                                        None
                                        
                                    # check if box is doubled
                                    current_boxes = [b for b in info[c].keys() if 'box' in b]
                                    for box in current_boxes:
                                        if box != b:
                                            same = True
                                            for var in list(info[c][b].keys()):
                                                if not info[c][box][var][0] == info[c][b][var][0]:
                                                    same = False
                                                    
                                                if not info[c][box][var][1] == info[c][b][var][1]:
                                                    same = False
                                                    
                                            if same:
                                                print('found double box --> delete it')
                                                del info[c][b]
                                                break
        
    return info
                    
                                
                    