#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 10:01:30 2024

@author: moritz
"""

import numpy as np
import sys

def shortest_edge(x,y,z):
    """
    compute the shortest edge of a box [x,y] determined by two vectors x and y
    in relation to a third vector z    

    Parameters
    ----------
    x : array
        lower vector for determining the box.
    y : array
        upper vector for determining the box.
    z : array
        vector for determining the relation of the edge lengths.

    Returns
    -------
    s : float
        relative shortest edge length of the box [x,y] relative to z.
    index : int
            representing the index of the shortest edge.

    """

    # check if input is correct
    if np.shape(x) != np.shape(y):
        print('shortest edge computation not possible: shapes do not align')
        sys.exit(1)

    if np.shape(x) != np.shape(z):
        print('shortest edge computation not possible: shapes do not align')
        sys.exit(1)
        
    if not (z > 0).all():
        print('shortest edge computation not possible: non positive relative \
              vector')
        sys.exit(1)
        
    # compute shortest edge and find index
    s = np.min(np.abs(x-y)/z)
    index = np.argmin(np.abs(x-y)/z)
    
    return s, index


# # test the function
# x = np.array([1,2,3,4])
# y = np.array([9,8,7,6])
# z = -1*np.ones(4)

# s, index = shortest_edge(x,y,z)
# print(s, index)    
