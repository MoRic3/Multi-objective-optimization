#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 09:17:57 2024

@author: moritz
"""

from pyomo.environ import *

import copy as cp
import numpy as np
import time


from compute_weight_hyperplane import *
from direct_image_box import *
from direct_search_routine import *
from initialize_local_bound_sets import *
from initialize_relaxation_info import *
from plot_enclosure import *
from plot_nondom import *
from plot_preimage_information import *
from plot_problem_counts import *
from plot_search_zone_counts import *
from plot_solution_times import *
from relaxed_image_box import *
from shortest_edge import *
from twostage_search_routine import *
from width_computation import *

def compute_enclosure(call_model, parameter, options):
    """
    routine for computing an enclosure of the nondominated set of a MOMINLP
    foundational pseudo code can be found in

    Eichfelder, G. and Link, M. and Volkwein, S. and Warnow, L.
    An adaptive relaxation-refinement scheme for multi-objective mixed-integer
    nonconvex opimization.
    2024.

    Algorithm 1.

    Parameters
    ----------
    call_model : function
        returning a pyomo model of the problem to be solved.
    parameter : structure
        containing all algorithm parameters.
    options : structure
        containing all optional settings for the algortihm.

    Returns
    -------
    encl_dict : dict
        containing all information collected by the algorithm.
    it : int
        iteration counter.

    """


    #%%%%
    # catch parameters and options

    # catch parameters
    m = parameter.m
    tol = parameter.tol
    maxiter = parameter.maxiter
    timeout = parameter.timeout
    factor_delta = parameter.factor_delta

    # check if relaxations should be used or not
    try:
        solve_direct = options.solve_direct
    except:
        print('relaxation based solution approach is applied')
        solve_direct = False

    try:
        tight_image_box = options.tight_image_box
    except:
        tight_image_box = False

    if solve_direct:
        # check if gap tolerance should be adapted
        try:
            gap_tolerance = options.gap_tolerance
        except:
            gap_tolerance = False

        # check the direct solver
        try:
            direct_solver = options.direct_solver
        except:
            direct_solver = 'scip'

        tight_image_box = True

    # choose vector for width measure
    try:
        dir_vec_option = options.direction
    except:
        print('standard width measure is chosen: all-one')
        dir_vec_option = 'classic'

    # check if plots should be shown
    try:
        show_plots = options.show_plots
    except:
        show_plots = False

    #%%%
    # initialize the information transmission dictionary

    # set up enclosure information dict
    encl_dict = {}
    encl_dict['factor_delta'] = factor_delta ###NEW!!!

    if not solve_direct:
        # initialize initial relaxation information
        model = call_model(0)
        info = initialize_relaxation_info(model)

    # determine if direct or two stage approach is chosen
    if tight_image_box:

        # check if gap tolerance should be adapted
        try:
            gap_tolerance = options.gap_tolerance
        except:
            gap_tolerance = False

        # check the direct solver
        try:
            direct_solver = options.direct_solver
        except:
            direct_solver = 'scip'

        # compute image box with directly solving the original problem
        encl_dict['zl'], encl_dict['zu'] = direct_image_box(
            call_model,
            m,
            gap_tolerance,
            direct_solver)

    else:
        # compute image box using the relaxed model
        encl_dict['zl'], encl_dict['zu'] = relaxed_image_box(
            call_model,
            m,
            info,
            options)

    if not solve_direct:
        # initialize relaxation dict
        encl_dict['lub_relaxation_information'] = {}
        encl_dict['lub_relaxation_information'][str(encl_dict['zu'])] = info

    # determine directon for width measure
    if dir_vec_option == 'relative':
        encl_dict['dir_vec'] = encl_dict['zu'] - encl_dict['zl']
    else:
        encl_dict['dir_vec'] = np.ones(m)

    # initialize local bound sets
    encl_dict['llbs'], encl_dict['Ldefpois'], encl_dict['lubs'], encl_dict['Udefpois']\
        = init_locbounds_defpois(encl_dict)

    # initialize set of potentially nondominated points
    encl_dict['N'] = []

    # initialize set of utopian points
    encl_dict['U'] = []

    # compute initial width
    width, worst_llb, worst_lub = compute_width(
        encl_dict['llbs'],
        encl_dict['lubs'],
        encl_dict['dir_vec'])

    # set up iteration count
    it = 0
    total_time = 0
    start_time = time.time()

    # set up analysis dict
    encl_dict['analysis'] = {}
    encl_dict['start_time'] = start_time
    encl_dict['timeout'] = timeout

    #%%%
    # start the algorithm

    while tol < width and it < maxiter and total_time < timeout:

        # print loop information
        print('\niteration # ', it, ' | current width:', round(width,3))

        # save current lubs assignment for loop
        old_lubs = cp.deepcopy(encl_dict['lubs'])
        old_Udefpois = cp.deepcopy(encl_dict['Udefpois'])

        # check if relaxation to image space information transmission is needed
        if not solve_direct:
            old_lub_rel_info = cp.deepcopy(encl_dict['lub_relaxation_information'])

        # set up iteration information dict
        encl_dict['analysis'][str(it)] = {}
        encl_dict['analysis'][str(it)]['solution_time'] = 0
        encl_dict['analysis'][str(it)]['problemcounter'] = 0
        encl_dict['analysis'][str(it)]['# of search zones closed'] = 0
        encl_dict['analysis'][str(it)]['# of search zones'] = 0

        if not solve_direct:
            encl_dict['analysis'][str(it)]['relaxedproblemcounter'] = 0
            encl_dict['analysis'][str(it)]['relaxed_solution_time'] = 0
            encl_dict['analysis'][str(it)]['preimageboxcounter'] = 0
            encl_dict['analysis'][str(it)]['maxpreimageboxes'] = 0
            encl_dict['analysis'][str(it)]['time bound tightening'] = 0
            encl_dict['analysis'][str(it)]['# of OBBT MILPs'] = 0
            encl_dict['analysis'][str(it)]['# of enforced feasibility check'] = 0
            encl_dict['analysis'][str(it)]['# of considered feasible'] = 0

        # start the loop through search zones
        for lub in old_lubs:

            # check if lub search zone has to be improved
            improved = True
            for llb in encl_dict['llbs']:
                if (llb < lub).all():
                    short_edge, index = shortest_edge(
                        llb,
                        lub,
                        encl_dict['dir_vec'])
                    if tol < short_edge:
                        improved = False
                        break

            if not improved:

                # count search zone visit
                encl_dict['analysis'][str(it)]['# of search zones'] += 1

                # check if solution in search zone exists
                alpha = compute_weight_hyperplane(lub, old_Udefpois)
                print('\nsearch zone determined by:', lub)

                if solve_direct:
                    # direct search routine without relaxations is applied
                    encl_dict = direct_search(
                        call_model,
                        lub - factor_delta * encl_dict['dir_vec'],
                        encl_dict,
                        alpha,
                        options,
                        it)

                else:
                    # relaxation based search routine is applied
                    lub_relaxation = old_lub_rel_info[str(lub)]

                    encl_dict = twostage_search(
                        call_model,
                        lub,
                        encl_dict,
                        alpha,
                        lub_relaxation,
                        options,
                        it)

            # check time limit
            mid_time = time.time()
            total_time = mid_time - start_time
            if total_time > timeout:
                break

        # compute new width
        width, worst_llb, worst_lub = compute_width(
            encl_dict['llbs'],
            encl_dict['lubs'],
            encl_dict['dir_vec'])

        # increase iteration count
        it += 1

    end_time = time.time()
    total_time = end_time - start_time
    encl_dict['total_time'] = total_time
    encl_dict['width'] = width
    
    if show_plots:

        if not solve_direct:
            print('\nsummary of analysis')
            print('total time:', total_time)
            print('maximal # of preimage set boxes:', max([encl_dict['analysis'][str(i)]['maxpreimageboxes'] for i in np.arange(0,it)]))
            print('AVG # of preimage set boxes:', sum(encl_dict['analysis'][str(i)]['preimageboxcounter'] for i in np.arange(0,it))/sum(encl_dict['analysis'][str(i)]['relaxedproblemcounter'] for i in np.arange(0,it)))
            print('# of MILPs:', sum(encl_dict['analysis'][str(i)]['relaxedproblemcounter'] for i in np.arange(0,it)))
            print('AVG time for MILPs:', sum(encl_dict['analysis'][str(i)]['relaxed_solution_time'] for i in np.arange(0,it))/sum(encl_dict['analysis'][str(i)]['relaxedproblemcounter'] for i in np.arange(0,it)))
            print('# of NLPs:', sum(encl_dict['analysis'][str(i)]['problemcounter'] for i in np.arange(0,it)))
            print('AVG time for NLPs:', sum(encl_dict['analysis'][str(i)]['solution_time'] for i in np.arange(0,it))/sum(encl_dict['analysis'][str(i)]['problemcounter'] for i in np.arange(0,it)))
            print('time spent for bound tightening:',
                  sum(encl_dict['analysis'][str(i)]['time bound tightening'] for i in np.arange(0,it)))
            print('# of OBBT MILPs:', sum(encl_dict['analysis'][str(i)]['# of OBBT MILPs'] for i in np.arange(0,it)))
            print('share of search zone improvement by feas-dec (total):',
                  sum(encl_dict['analysis'][str(i)]['# of considered feasible'] for i in np.arange(0,it))/sum(encl_dict['analysis'][str(i)]['# of search zones'] for i in np.arange(0,it)))
            for i in np.arange(0,it):
                print('share of search zone improvement by feas-dec in', i,'-th iteration:', encl_dict['analysis'][str(i)]['# of considered feasible']/encl_dict['analysis'][str(i)]['# of search zones'])
            print('share of enforced search zone improvement (total):',
                  sum(encl_dict['analysis'][str(i)]['# of enforced feasibility check'] for i in np.arange(0,it))/sum(encl_dict['analysis'][str(i)]['# of search zones'] for i in np.arange(0,it)))
            for i in np.arange(0,it):
                print('share of enforced search zone improvement in', i,'-th iteration:', encl_dict['analysis'][str(i)]['# of enforced feasibility check']/encl_dict['analysis'][str(i)]['# of search zones'])

            plot_nondom(encl_dict['N'], m, total_time, it, tol, width)
            plot_enclosure(encl_dict, m, total_time, it, tol, width)
            plot_preimage_information(encl_dict['analysis'], it)
            plot_solution_times(encl_dict['analysis'],it)
            plot_problem_counts(encl_dict['analysis'],it)
            plot_search_zone_count(encl_dict['analysis'], it)

        else:
            plot_nondom(encl_dict['N'], m, total_time, it, tol, width)
            plot_enclosure(encl_dict, m, total_time, it, tol, width)
            
    return encl_dict, it
