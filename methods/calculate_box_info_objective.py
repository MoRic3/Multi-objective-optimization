#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 13:59:51 2024

@author: moritz
"""

from pyomo.environ import *

from compute_least_square_weight import *
from compute_overest_error_objective import *

def calculate_box_info_objective(o, vars, info, call_model):
    """
    routine for calculating the information needed for setting up
    a piecewise linear relaxation on a subbox of the objective
    function, i.e., we need to compute an underestimator and
    therefore the overestimation error

    Parameters
    ----------
    o : pyomo objective object
        representing the objective for which the information should
        be calculated.
    vars : list
        containing pyomo variable objects appearing in the objective
        function of interest.
    info : dict
        containing all information of the current box of interest.
    call_model : function
        returning a pyomo model of the problem to be solved.

    Returns
    -------
    info : dict
        containing all information to set up a piecewise linear relaxation
        on the current box of interest.

    """
    
    # compute least square weight determiming the piecewise linear function
    info['weight'] = compute_least_square_weight(o, vars, info)
    
    # compute the overestimation error of the piecewise linear function
    info['overest_error'] = compute_overest_error_objective(call_model,
                                                            o,
                                                            vars,
                                                            info)
    
    return info
