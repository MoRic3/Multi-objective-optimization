#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 10:23:02 2024

@author: moritz
"""

import copy as cp
import numpy as np
import sys

from shortest_edge import *

def compute_width(llbs, lubs, dir_vec):
    """
    routine for computing the relative width of the current enclosure 
    determined by lubs and llbs w.r.t. the vector dir_vec.
    
    For reference see:
        
    Eichfelder, G. and Kirst, P. and Meng, L. and Stein, O.
    A general Branch-And-Bound framework for continuous global multi-objective
    optimization. J. Global Optim. 80. 2021.

    Parameters
    ----------
    llbs : list of arrays
        consisting of current assignement of local lower bounds.
    lubs : list of arrays
        consisting of current assignment of local lower bounds.
    dir_vec : array
        determining the magnitudes for relative width computation.

    Returns
    -------
    width : float
            representing the relative width of the enclosure.
    worst_llb : array
                representing the lower corner of the box where width is attained
    worst_lub : array
                representing the upper corner of the box where width is attained

    """
    
    # start the loop
    width = 0
    for llb in llbs:
        for lub in lubs:
            
            # check if shapes do align
            if np.shape(llb) != np.shape(lub):
                print('width computation not possible: shapes do not align')
                sys.exit(1)

            # check if llb and lub determine a box
            if (llb < lub).all():
                s, j = shortest_edge(llb, lub, dir_vec)

                # check if box width increases current width
                if width < s:
                    width = s
                    worst_lub = cp.copy(lub)
                    worst_llb = cp.copy(llb)
    
    return width, worst_llb, worst_lub


# # test the function
# llbs = [np.array([1,2,3]), np.array([3,2,1])]
# lubs = [np.array([4,5,6]), np.array([7,8,9])]
# dir_vec = np.ones(3)

# w, w_llb, w_lub = compute_width(llbs, lubs, dir_vec)
# print(w, w_llb, w_lub)                    