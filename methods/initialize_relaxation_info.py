#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 14:33:03 2024

@author: moritz
"""

from pyomo.environ import *
from pyomo.core.expr.current import identify_variables

def initialize_relaxation_info(model):
    """
    routine for initializing the relaxation information of the problem instance
    'model'

    Parameters
    ----------
    model : pyomo model
        representing the problem instance of interest.

    Returns
    -------
    info : dict
        containing all information for setting up a piecewise linear 
        relaxation of the problem of interest.

    """
    
    # initialize dict
    info = {}
    info['bounds'] = {}
    
    # get nonlinear constraints
    nonlin_cons = [c for c in model.component_objects(Constraint) if c.body.polynomial_degree() != 1]
    
    # get nonlinear objectives
    nonlin_objectives = [o for o in model.component_objects(Objective) if o.polynomial_degree() != 1]

    # for nonlinear constraints
    for c in nonlin_cons:
        vars = list(identify_variables(c.body))
        info[c.name] = {}
        info[c.name]['box0'] = {}
        for v in vars:
            if v.is_indexed():
                for i in v.index_set():
                    info[c.name]['box0'][v[i].name] = [v[i].lb, v[i].ub]
                    
                    if v[i].name not in info['bounds'].keys():
                        info['bounds'][v[i].name] = [v[i].lb, v[i].ub]
                        if v[i].domain == Integers or v[i].domain == Binary:
                            info['bounds'][v[i].name].append('discrete')
            
            else:
                info[c.name]['box0'][v.name] = [v.lb, v.ub]
                
                if v.name not in info['bounds'].keys():
                    info['bounds'][v.name] = [v.lb, v.ub]
                    if v.domain == Integers or v.domain == Binary:
                        info['bounds'][v.name].append('discrete')
    
    # for nonlinear objectives
    for o in nonlin_objectives:
        vars = list(identify_variables(o.expr))
        info[o.name] = {}
        info[o.name]['box0'] = {}
        for v in vars:
            if v.is_indexed():
                for i in v.index_set():
                    info[o.name]['box0'][v[i].name] = [v[i].lb, v[i].ub]
                    
                    if v[i].name not in info['bounds'].keys():
                        info['bounds'][v[i].name] = [v[i].lb, v[i].ub]
                        if v[i].domain == Integers or v[i].domain == Binary:
                            info['bounds'][v[i].name].append('discrete')
            
            else:
                info[o.name]['box0'][v.name] = [v.lb, v.ub]
                
                if v.name not in info['bounds'].keys():
                    info['bounds'][v.name] = [v.lb, v.ub]
                    if v.domain == Integers or v.domain == Binary:
                        info['bounds'][v.name].append('discrete')
    
    # initialize BT counter
    info['BT counter'] = 0
    
    return info