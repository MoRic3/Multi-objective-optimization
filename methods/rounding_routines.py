#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 15:02:04 2024

@author: moritz
"""

import numpy as np
import sys

def rounding_lower(x, digits=10):
    """
    routine for rounding a float to certain number of digits while ensuring
    that the new float is smaller than the original number

    Parameters
    ----------
    x : float
        representing the original number.
    digits : int, optional
        representing the number of digits that are allowed. The default is 10.

    Returns
    -------
    x_new : float
        representing the rounded number.

    """
    
    # start with rounding function
    x_new = np.round(x, digits)
    
    # check if rounded number is larger than original number
    if x_new > x:
        x_new -= 10**-digits
        x_new = np.round(x_new,digits)
    
    # check if after correction rounded number is still larger than original
    if x_new > x:
        print('lower rounding did not work properly')
        return x
    
    return x_new


def rounding_upper(x, digits=10):
    """
    routine for rounding a float to certain number of digits while ensuring
    that the new float is larger than the original number

    Parameters
    ----------
    x : float
        representing the original number.
    digits : int, optional
        representing the number of digits that are allowed. The default is 10.

    Returns
    -------
    x_new : float
        representing the rounded number.

    """
    
    # start with rounding function
    x_new = np.round(x, digits)
    
    # check if rounded number is smaller than original number
    if x_new < x:
        x_new += 10**-digits
        x_new = np.round(x_new,digits)
    
    # check if after correction rounded number is still smaller than original
    if x_new < x:
        print('upper rounding did not work properly')
        return x
        
    return x_new