#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 11:06:50 2024

@author: moritz
"""

from pyomo.environ import *

from compute_least_square_weight import *
from compute_overest_error import *
from compute_underest_error import *

def calculate_box_info(c, vars, info, call_model):
    """
    routine for calculation the information needed for setting up
    a piecewise linear relaxation on a subbox of a constraint
    function

    Parameters
    ----------
    c : pyomo constraint object
        representing the constraint function for which the
        informaton should be calculated.
    vars : lis
        containing pyomo variable objects appearing in the 
        constraint function of interest.
    info : dict
        containing all information of the current box of interest.
    call_model : function
        returning a pyomom model of the problem to be solved.

    Returns
    -------
    info : dict
        containing all information to set up a piecewise linear 
        relaxation on the current box of interest.

    """
    
    # compute least square weight determining the piecewise linear funtion
    info['weight'] = compute_least_square_weight(c, vars, info)
    
    # check if overestimation error is needed for setting up an
    # underestimation function
    if c.ub != None:
        info['overest_error'] = compute_overest_error(call_model,
                                                      c,
                                                      vars,
                                                      info)
        
    # check if underestimation error is needed for setting up an
    # overestimation function
    if c.lb != None:
        info['underest_error'] = compute_underest_error(call_model,
                                                        c,
                                                        vars,
                                                        info)
    return info
