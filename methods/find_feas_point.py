#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 10:00:06 2024

@author: moritz
"""

from pyomo.environ import *

import numpy as np

from restricted_weighted_sum_feas import *
from update_llbs import *
from update_lubs import *
from update_lub_rel_info import *
from update_nondom import *


def find_feas_point(call_model, encl_dict, u, alpha, options, info, it):
    """
    routine for enforced finding of a feasible point in a search zone
    determined by the image space vector u

    Parameters
    ----------
    call_model : function
        returning a pyomo model of the problem to be solved.
    encl_dict : dict
        containing all information collected by the algorithm.
    u : ndarray
        representing the local upper bound determining the search zone.
    alpha : ndarray
        containing the specific weight for each of the objective functions.
    options : structure
        containing all optional settings for the algorithm.
    info : dict
        containing all information for setting up the current piecewise
        linear relaxation.
    it : int
        determining the current iteration.

    Returns
    -------
    encl_dict : dict
        containing all information collected by the algorithm.
    info : dict
        containing all information for setting up the current piecewise
        linear relaxation.
    improved : boolean
        indicating if current search zone was improved or not.

    """
    
    # check if bound tightening should be enforced for the upcoming
    # refinement step
    try:
        enforced_BT = options.enforced_BT
    except:
        enforced_BT = False
    
    # solve the weighted sum problem to feasibility
    model = call_model(0)
    solvec, feasible_solution, sol_time = restricted_weighted_sum_feas(
        model,
        len(alpha),
        alpha,
        u - encl_dict['factor_delta'] * encl_dict['dir_vec'],
        options)
    
    # check for feasibility
    if isinstance(solvec, np.ndarray):
        
        print('enforcedly found potentially nondominated point:', solvec)
        
        # update set of potentially nondominated points
        encl_dict['N'], check = update_nondom(encl_dict['N'], solvec)
        
        old_lubs = cp.deepcopy(encl_dict['lubs'])
        
        # update set of lubs
        encl_dict['lubs'], encl_dict['Udefpois'] = update_lubs(
            encl_dict['lubs'],
            encl_dict['Udefpois'],
            solvec)
        
        # eventually enforce bound tightening in next refinement step
        if enforced_BT:
            info['BT counter'] = 1e20
        
        # update lub relaxation information
        encl_dict['lub_relaxation_information'] = update_lub_rel_info(
            encl_dict,
            info,
            u,
            old_lubs)
        
        improved = True
    
    # if search zone is empty
    else:
        print('search zone is empty')
        encl_dict['llbs'], encl_dict['Ldefpois'] = update_llbs(
            encl_dict['llbs'],
            encl_dict['Ldefpois'],
            u - encl_dict['factor_delta'] * encl_dict['dir_vec'])

        improved = True
        
    return encl_dict, info, improved
            