#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 15:18:46 2024

@author: moritz
"""

from pyomo.environ import *

from rebuild_utopian_llbs import *
from refinement_routine import *
from restricted_reduced_weighted_sum import *
from update_llbs import *
from update_lubs import *
from update_lub_rel_info import *
from update_nondom import *
from update_utopian import *


def find_points(call_model, y, solution, relaxation_errors, encl_dict, u, alpha, options, info, it):
    """
    routine for finding a potentially nondominated point in the search zone
    determined by 'u' based on the solution 'solution' of the relaxed problem
    foundational pseudo code can be found in
    
    Eichfelder, G. and Link, M. and Volkwein, S. and Warnow, L.
    An adaptive relaxation-refinement scheme for multi-objective mixed-integer
    nonconvex opimization.
    2024.
    
    Algorithm 3.

    Parameters
    ----------
    call_model : function
        returning a pyomo model of the problem to be solved.
    y : ndarray
        representing the utopian point coming from ilving the relaxed problem.
    solution : dict
        having the variable names as keys and the corresponding optimal values
        as values.
    relaxation_errors : dict
        having the constraint names as keys and the corresponding constraint
        satisfaction errors as values.
    encl_dict : dict
        containing all information collected by the algorithm.
    u : ndarray
        representing the local upper bound determining the search zone.
    alpha : ndarray
        containing the specific weight for each of the objective functions.
    options : structure
        containing all optional settings for the algorithm.
    info : dict
        containing all information for setting up the piecewise linear
        relaxation of the problem of interest.
    it : int
        determining the current iteration number.

    Returns
    -------
    encl_dict : dict
        containing all information collected by the algorithm.
    info : dict
        containing all information for setting up the piecewise linear 
        relaxation of the problem of interest.
    improved : boolean
        indicating if current search zone was improved or not.

    """
    
    # catch absolute relaxation tolerance
    try:
        constraint_tolerance = options.constraint_tolerance
    except:
        constraint_tolerance = 5e-3
    
    # check if relaxed solution can be considered feasible
    if relaxation_errors['max_error'] < constraint_tolerance:
        print('relaxed solution is considered as feasible')
        
        # update utopian points
        encl_dict['U'], check = update_utopian(encl_dict['U'], y, options)
        
        # check if new nondominated point dominates utopians
        if check == 0:
            print('nondominated point dominates utopians --> rebuild')
            encl_dict = rebuild_utopian_llbs(encl_dict, y)
            
        else:
            encl_dict['llbs'], encl_dict['Ldefpois'] = update_llbs(
                encl_dict['llbs'],
                encl_dict['Ldefpois'],
                y)
        
        # update set of potentially nondominated points
        encl_dict['N'], check = update_nondom(encl_dict['N'], y)
        
        # secure old lub dict
        old_lubs = cp.deepcopy(encl_dict['lubs'])
        
        # update set of lubs
        encl_dict['lubs'], encl_dict['Udefpois'] = update_lubs(
            encl_dict['lubs'],
            encl_dict['Udefpois'],
            y)
        
        # update lub relaxation information
        encl_dict['lub_relaxation_information'] = update_lub_rel_info(
            encl_dict,
            info,
            u,
            old_lubs)
        
        encl_dict['analysis'][str(it)]['# of considered feasible'] += 1
        
        improved = True
    
    else:
        # update utopians
        encl_dict['U'], check = update_utopian(encl_dict['U'], y, options)
        
        # check if relaxed solution improves utopians
        if check == 0:
            print('relaxed image point does not improve utopians --> refine')
            
            info, tighten_time, tighten_counter = refinement_routine(
                call_model,
                solution,
                relaxation_errors,
                info,
                u,
                options)
        
            encl_dict['analysis'][str(it)]['time bound tightening'] += tighten_time
            encl_dict['analysis'][str(it)]['# of OBBT MILPs'] += tighten_counter
            improved = False
        
        else:
            encl_dict['llbs'], encl_dict['Ldefpois'] = update_llbs(
                encl_dict['llbs'],
                encl_dict['Ldefpois'],
                y)
            
            solvec, feasible_solution, sol_time = restricted_reduced_weighted_sum(
                call_model,
                len(alpha),
                alpha,
                solution,
                u - encl_dict['factor_delta'] * encl_dict['dir_vec'],
                options)
            
            encl_dict['analysis'][str(it)]['solution_time'] += sol_time
            encl_dict['analysis'][str(it)]['problemcounter'] += 1
            
            if isinstance(solvec, np.ndarray):
                print('found potentially nondominated point:', solvec)
                
                # update set of potentially nondominated points
                encl_dict['N'], check = update_nondom(encl_dict['N'], solvec)
                
                # secure old lub dict
                old_lubs = cp.deepcopy(encl_dict['lubs'])
                
                # update set of lubs
                encl_dict['lubs'], encl_dict['Udefpois'] = update_lubs(
                    encl_dict['lubs'],
                    encl_dict['Udefpois'],
                    solvec)
                
                # update lub relaxation information
                encl_dict['lub_relaxation_information'] = update_lub_rel_info(
                    encl_dict,
                    info,
                    u,
                    old_lubs)
                
                improved = True

            else:
                print('reduced problem infeasible --> refine')
                
                info, tighten_time, tighten_counter = refinement_routine(
                    call_model,
                    solution,
                    relaxation_errors,
                    info,
                    u,
                    options)
                
                encl_dict['analysis'][str(it)]['time bound tightening'] += tighten_time
                encl_dict['analysis'][str(it)]['# of OBBT MILPs'] += tighten_counter
                improved = False                
            
        
    return encl_dict, info, improved
            