#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 10:32:31 2024

@author: moritz
"""

from pyomo.environ import *

import copy as cp

from build_corner_dict import *

def compute_least_square_weight(cons, vars, info):
    """
    routine for computing the least square weight of a linear function
    with respect to the corner points of a variable domain box and
    a constraint function

    Parameters
    ----------
    cons : pyomo constraint object
        representing the constraint function for which the least square
        weight should be computed.
    vars : list
        containing pyomo variable objects appearing the constraint
        function of interest.
    info : dict
        containing all information of the current box of interest.

    Returns
    -------
    weight : ndarray
        containing respective weights for all appearing variables
        as well as the constant term.

    """
    
    n = len(vars)
    
    # iterate until suitable system is found
    while True:
        
        # generate corner points
        points = generate_corner_dict(info)
        
        # set up the system
        A = np.zeros((len(points.keys()), n+1))
        b = np.zeros(len(points.keys()))
        for i in points.keys():
            j = 0
            for v in vars:
                v.fix(points[i][v.name], skip_validation=True)
                # v = points[i][v.name]
                A[i,j] = cp.deepcopy(points[i][v.name])
                j += 1
            b[i] = value(cons)
        A[:,-1] = np.ones(len(points.keys()))
        
        # check if everything went well
        try:
            weight_vector = np.linalg.lstsq(A,b,rcond=None)[0]
            break
        # repreat if not
        except:
            weight_vector = np.zeros(n+1)
            break

    # set up weight dictionary
    weight = {}
    j = 0
    for v in vars:
        weight[v.name] = cp.deepcopy(np.round(weight_vector[j],6))
        v.fixed = False
        j += 1
    
    weight['constant'] = np.round(weight_vector[-1],6)
    
    return weight