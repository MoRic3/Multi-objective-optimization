#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 16:23:07 2024

@author: moritz
"""

import copy as cp


def update_lub_rel_info(encl_dict, info, u, old_lubs):
    """
    routine for assigning preimage space relaxation information to the incoming
    local upper bounds

    Parameters
    ----------
    encl_dict : dict
        containing all information collected by the algorithm.
    info : dict
        containing all information for setting up the current piecewise linear
        relaxation of the problem of interest.

    Returns
    -------
    encl_dict['lub_relaxation_information'] : dict
        having the currently active lubs as keys and the corresponding 
        relaxation information dicts as values.

    """
    
    old_info_dict = cp.deepcopy(encl_dict['lub_relaxation_information'])
    
    encl_dict['lub_relaxation_information'] = {}
    for lub in encl_dict['lubs']:
        try:
            encl_dict['lub_relaxation_information'][str(lub)] = cp.deepcopy(
                old_info_dict[str(lub)])
        except:
            if (lub <= u).all():
                encl_dict['lub_relaxation_information'][str(lub)] = cp.deepcopy(
                    info)
                # increase count for new lubs since last OBBT application
                encl_dict['lub_relaxation_information'][str(lub)]['BT counter'] += 1
        
            else:
                for old_lub in old_lubs:
                    if (lub <= old_lub).all():
                        encl_dict['lub_relaxation_information'][str(lub)] = cp.deepcopy(
                            old_info_dict[str(old_lub)])
                        # increase count for new lubs since last OBBT application
                        encl_dict['lub_relaxation_information'][str(lub)]['BT counter'] += 1
                        break
    
    return encl_dict['lub_relaxation_information']