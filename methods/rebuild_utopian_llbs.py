#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 16:12:54 2024

@author: moritz
"""

import copy as cp

from initialize_local_bound_sets import *
from update_llbs import *

def rebuild_utopian_llbs(encl_dict, y):
    """
    routine for rebuilding the set of utopian points and corresponding set
    of local lower bounds w.r.t. a considered-as-feasible point which dominates
    at least one of the utopian points

    Parameters
    ----------
    encl_dict : dict
        containing all information collected by the algorithm.
    y : ndarray
        representing the considered-as-feasible point.

    Returns
    -------
    encl_dict : dict
        containing all updated information collected by the algorithm.

    """

    # save old and initalize new encl_dict
    old_encl_dict = cp.deepcopy(encl_dict)
    encl_dict = {}
    encl_dict['zl'] = cp.deepcopy(old_encl_dict['zl'])
    encl_dict['zu'] = cp.deepcopy(old_encl_dict['zu'])
    encl_dict['dir_vec'] = cp.deepcopy(old_encl_dict['dir_vec'])
    encl_dict['factor_delta'] = cp.deepcopy(old_encl_dict['factor_delta'])
    encl_dict['N'] = cp.deepcopy(old_encl_dict['N'])

    encl_dict['llbs'], encl_dict['Ldefpois'], encl_dict['lubs'], encl_dict['Udefpois']\
        = init_locbounds_defpois(encl_dict)

    encl_dict['lubs'] = cp.deepcopy(old_encl_dict['lubs'])
    encl_dict['Udefpois'] = cp.deepcopy(old_encl_dict['Udefpois'])
    encl_dict['lub_relaxation_information'] = cp.deepcopy(old_encl_dict['lub_relaxation_information'])
    encl_dict['analysis'] = cp.deepcopy(old_encl_dict['analysis'])
    encl_dict['start_time'] = cp.deepcopy(old_encl_dict['start_time'])
    encl_dict['timeout'] = cp.deepcopy(old_encl_dict['timeout'])

    # rebuild utopians
    encl_dict['U'] = []

    for x in old_encl_dict['U']:
        if not (y <= x).all():
            encl_dict['U'].append(x)

    # check if y is part of U
    include = True
    for x in encl_dict['U']:
        if (y == x).all():
            include = False

    if include:
        encl_dict['U'].append(y)

    # iteratively update llbs and Ldefpois
    for x in encl_dict['U']:
        encl_dict['llbs'], encl_dict['Ldefpois'] = update_llbs(
            encl_dict['llbs'],
            encl_dict['Ldefpois'],
            x)

    return encl_dict
