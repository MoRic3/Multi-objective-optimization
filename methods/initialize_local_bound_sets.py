#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 09:29:04 2024

@author: moritz
"""

import copy as cp
import numpy as np

def init_locbounds_defpois(encl_dict):
    """
    routine for initializing lists of local lower and upper bound lists
    together with respective dicts of defining points

    Parameters
    ----------
    encl_dict : dict
        containing all information collected by the algorithm.

    Returns
    -------
    llbs : list
        consisting of initial assignment of local lower bounds.
    Ldefpois : dict
        consisting of defining points for any component of any currently
        valid local lower bound.
    lubs : list
        consisting of initial assignment of local upper bounds.
    Udefpois : dict
        consisting of defining points for any component of any currently
        valid local upper bound.

    """
    
    zl, zu = encl_dict['zl'], encl_dict['zu']
    
    # initialize list of local upper bounds
    lubs = [zu]
    
    # initialize dict of defining points for local upper bounds
    Udefpois = {}
    Udefpois[str(zu)] = {}
    for i in np.arange(0,len(zu)):
        d = cp.deepcopy(zl)
        d[i] = cp.deepcopy(zu[i])
        Udefpois[str(zu)][i] = [d]
        
    # initialize list of local lower bounds
    llbs = [zl]
    
    # initialize list of defining points for local lower bound
    Ldefpois = {}
    Ldefpois[str(zl)] = {}
    for i in np.arange(0,len(zl)):
        d = cp.deepcopy(zu)
        d[i] = cp.deepcopy(zl[i])
        Ldefpois[str(zl)][i] = [d]
    
    return llbs, Ldefpois, lubs, Udefpois