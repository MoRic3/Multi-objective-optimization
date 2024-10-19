#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 15:20:20 2024

@author: moritz
"""

import numpy as np

def compute_weight_hyperplane(u, defpois):
    """
    routine for computing weight vector corresponding to connecting hyperplane
    determined by defining points of current search zone local upper bound u

    Parameters
    ----------
    u : array
        representing current search zone local upper bound.
    defpois : dict
        consisting of defining points for any local upper bound.

    Returns
    -------
    alpha : array
        representing the weight vector for weighted sum method.

    """
    
    # catch dimension
    m = len(u)
    
    # set up linear system
    A = np.eye(m)
    b = np.ones(m)
    for i in np.arange(0,m):
        A[i,:] = defpois[str(u)][i][-1]
        
    # try to solve the system
    try:
        alpha = np.linalg.solve(A,b)
    except:
        alpha = np.ones(m)
    
    # normalize solution
    alpha = np.abs(alpha/np.linalg.norm(alpha,ord=1))
    
    return alpha