#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 14:22:23 2024

@author: moritz
"""

import numpy as np
import sys

def update_utopian(U, y, options):
    """
    update the stable set of utopian points w.r.t. a new utopian point
    
    for reference see Algorithm 4 in
    
    Link, M. and Volkwein, S. 
    Adaptive piecewise linear relaxations for enclosure computations for
    nonconvex multi-objective mixed-integer quadratically constrained programs
    J. Global Optim. 87. 2023.

    Parameters
    ----------
    U : list
        consisting of a stable set of utopian points.
    y : array
        the new utopian points.
    options : structure
        consisting of possible options for procedure 

    Returns
    -------
    new_U : list
        updated list of utopian points.
    check :  boolean
        indicating if y belongs to updated list of utopian points, i.e, if y 
        improved U

    """
    
    # decide if it should be called a "successful" update if y already belonged
    # to U (if soft_utopian_check) or not (if not utopian_check)
    try:
        soft_utopian_check = options.soft_utopian_check
    except:
        soft_utopian_check = False
    
    # check if U is nonempty
    if len(U) == 0:
        new_U = [y]
        check = 1
        return new_U, check
    
    else:
        # intialize new list of utopian points
        new_U = []
        
        # go through points
        check = 1
        for x in U:
            # check shapes
            if np.shape(x) != np.shape(y):
                print('update of utopian points not possible: shapes do not\
                      align')
                sys.exit(1)
            
            # check if y already belongs to U
            if (y == x).all():
                new_U = U
                if soft_utopian_check:
                    check = 1
                else:
                    check = 0
                return new_U, check
            
            # check if y dominates x
            elif (y <= x).all():
                new_U.append(x)
                check = 0
            
            # check if y is not weakly dominated by x 
            elif (y < x).any():
                new_U.append(x)
        
        if check == 1:
            new_U.append(y)
    
    return new_U, check