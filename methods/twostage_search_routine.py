#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 14:27:28 2024

@author: moritz
"""

import numpy as np
import time

from find_feas_point import *
from find_points import *
from relax_model import *
from restricted_relaxed_weighted_sum import *
from update_llbs import *

def twostage_search(call_model, u, encl_dict, alpha, info, options, it):
    """
    routine for performing a two-stage search -- first solving a piecewise 
    linear relaxation, and then a reduced problem -- for the search zone
    determined by the local upper bound 'u'

    Parameters
    ----------
    call_model : function
        returning a pyomo model of the problem to be solved.
    u : ndarray
        representing the image space vector determining the search zone.
    encl_dict : dict
        containing all information collected by the algorithm.
    alpha : ndarray
        contains specific weight for each of the objective functions.
    info : dict
        containing all information for setting up the current piecewise linear
        relaxation of the problem of interest.
    options : structure
        containing all optional settings for the algorithm.
    it : int
        representing the current iteration.

    Returns
    -------
    encl_dict : dict
        containing all updated information collected by the algorithm.

    """

    # catch milp solver
    try:
        milp_solver = options.milp_solver
    except:
        milp_solver = 'gurobi'

    # catch upper bound on refinement steps before looking for feasible point
    try:
        refine_until_feasible_search = options.refine_until_feasible_search
    except:
        refine_until_feasible_search = 1e20

    # catch image space dimension
    m = len(u)

    improved = False
    
    # intialize counter for refinement steps
    count = 0
    
    while not improved:
        # build relaxed problem
        model = call_model(0)
        model, info, box_counter = relax_model(model, call_model, info)

        # solve relaxed weighted sum problem
        solvec, solution, relaxation_errors, sol_time = restricted_relaxed_weighted_sum(
            model,
            m,
            alpha,
            u - encl_dict['factor_delta'] * encl_dict['dir_vec'],
            options)

        encl_dict['analysis'][str(it)]['relaxedproblemcounter'] += 1
        encl_dict['analysis'][str(it)]['relaxed_solution_time'] += sol_time
        encl_dict['analysis'][str(it)]['preimageboxcounter'] += box_counter
        encl_dict['analysis'][str(it)]['maxpreimageboxes'] = max(box_counter,
                         encl_dict['analysis'][str(it)]['maxpreimageboxes'])

        if isinstance(solvec, np.ndarray):
            print('found possible new lower bound:', solvec)

            encl_dict, info, improved = find_points(
                call_model,
                solvec,
                solution,
                relaxation_errors,
                encl_dict,
                u,
                alpha,
                options,
                info,
                it)

        else:
            print('search zone is empty')
            encl_dict['llbs'], encl_dict['Ldefpois'] = update_llbs(
                encl_dict['llbs'],
                encl_dict['Ldefpois'],
                u - encl_dict['factor_delta'] * encl_dict['dir_vec'])

            encl_dict['analysis'][str(it)]['# of search zones closed'] += 1
            improved = True

        if count >= refine_until_feasible_search and not improved:
            encl_dict, info, improved = find_feas_point(
                call_model,
                encl_dict,
                u,
                alpha,
                options,
                info,
                it)
            
            # count enforced feasibility check
            encl_dict['analysis'][str(it)]['# of enforced feasibility check'] += 1

        search_time = time.time()
        print('elapsed time:', search_time - encl_dict['start_time'])
        if search_time - encl_dict['start_time'] >= encl_dict['timeout']:
            break

        count += 1
        
    return encl_dict
