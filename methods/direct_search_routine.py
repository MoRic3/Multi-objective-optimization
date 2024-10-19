 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 10:00:37 2024

@author: moritz
"""

import copy as cp
import numpy as np

import time

from restricted_weighted_sum import *
from update_llbs import *
from update_lubs import *
from update_nondom import *

def direct_search(call_model, u, encl_dict, alpha, options, it):
    """
    routine for tackling a search zone determined by a local upper bound 
    directly. That is, looking for a nondominated point of the problem 
    determined by call_model and afterwards updating the respective set local
    lower and upper bounds together with defining points.

    Parameters
    ----------
    call_model : function
        returning a pyomo model of the problem to be solved.
    u : array
        representing the restrictions on the objective function components.
    encl_dict : dict
        containing all information collected by the algorithm
    alpha : array
        containing the specific weight for each of the objective functions.
    options : structure
        containing all optional settings for the algorithm.
    it : int
        determining the current iteration

    Returns
    -------
    encl_dict: dict
        containing all information collected by the algorithm
    """
    
    # catch infos
    dir_vec = cp.deepcopy(encl_dict['dir_vec'])
    
    # check if gap tolerance should be adapted
    try:
        tol = options.gap_tolerance
    except:
        tol = False
    
    # catch solver for direct problem
    try:
        solver = options.direct_solver
    except:
        solver = 'scip'
    
    # get image space dimension
    m = len(u)
    
    # set up model
    model = call_model(0)
    
    # solve the restricted weighted sum problem
    solvec, solution, sol_time = restricted_weighted_sum(model,
                                          m,
                                          alpha,
                                          u,
                                          tol,
                                          solver)

    encl_dict['analysis'][str(it)]['solution_time'] += sol_time
    encl_dict['analysis'][str(it)]['problemcounter'] += 1

    # check if new nondominated point is found
    if isinstance(solvec, np.ndarray):
        print('found new potentially nondominated point:', solvec)
        
        # update sets
        encl_dict['N'], check = update_nondom(encl_dict['N'], solvec)
        
        if tol:
            encl_dict['llbs'], encl_dict['Ldefpois'] = update_llbs(
                encl_dict['llbs'],
                encl_dict['Ldefpois'],
                solvec - tol*dir_vec)
        else:
            encl_dict['llbs'], encl_dict['Ldefpois'] = update_llbs(
                encl_dict['llbs'],
                encl_dict['Ldefpois'],
                solvec)
            
        encl_dict['lubs'], encl_dict['Udefpois'] = update_lubs(
            encl_dict['lubs'],
            encl_dict['Udefpois'],
            solvec)
        
    # if search zone is empty
    else:
        print('search zone is empty')
        encl_dict['llbs'], encl_dict['Ldefpois'] = update_llbs(
            encl_dict['llbs'],
            encl_dict['Ldefpois'],
            u)
        
    return encl_dict