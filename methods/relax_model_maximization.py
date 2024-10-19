#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 12:23:23 2024

@author: moritz
"""

from pyomo.environ import *
from pyomo.core.expr.current import identify_variables

from calculate_box_info import *
from calculate_box_info_objective_max import *

def relax_model_maximization(model, call_model, info):
    """
    routine for setting up a piecewise linear relaxation of the original model
    of interest suitable for maximization, i.e., instead of an underestimation
    function for the nonlinear objectives, an overestimation function is needed

    Parameters
    ----------
    model : pyomo model
        representing the problem instance of interest.
    call_model : function
        returning a pyomo model of the problem to be solved.
    info : dict
        containing all information for setting up the current piecewise linear
        relaxation of the problem of interest.

    Returns
    -------
    model : pyomo model
        representing the piecewise linear relaxation of the original problem 
        of interest.
    info : dict
        containing all information for setting up the current piecewise linear
        relaxation of the problem of interest.
    box_counter : int
        representing the number of preimage set boxes appearing in the current
        piecewise linear relaxation.

    """
    box_counter = 0
    
    # catch nonlinear constraints
    nonlin_cons = [c for c in model.component_objects(Constraint) if c.body.polynomial_degree() != 1]
    for c in nonlin_cons:
        # catch variables appearing in constraint
        vars = list(identify_variables(c.body))
        
        # catch boxes for constraint and introduce binaries
        boxes = [b for b in info[c.name].keys() if 'box' in b]
        
        number_of_boxes = len(boxes)
        box_counter += number_of_boxes
        
        model.add_component(c.name+'_box_set', RangeSet(0,number_of_boxes-1))
        for s in model.component_objects(RangeSet):
            if s.name == c.name+'_box_set':
                model.add_component(c.name+'_box_binaries',
                                    Var(s, within=Binary))
        
        
        # define SOS1 constraint
        var_list = list(model.component_objects(Var))
        var_list.reverse()
        for bina in var_list:
            if bina.name == c.name+'_box_binaries':
                model.add_component(c.name+'_sos_cons',
                                    SOSConstraint(var=bina, sos=1))
                model.add_component(c.name+'_only_one_active',
                                    Constraint(expr=quicksum(bina[i] for i in
                                                     bina.index_set()) == 1))
                break
            
        # introduce relaxation for each box
        i = 0
        for b in boxes:
            # check if calculations for box need to be done
            if 'weight' not in info[c.name][b].keys():
                info[c.name][b] = calculate_box_info(c,
                                                     vars,
                                                     info[c.name][b],
                                                     call_model)
            
            # determine active partition and set variable bounds
            for v in vars:
                model.add_component(
                    'active_upper_of_'+v.name+'_for_'+b+'_wrt_'+c.name,
                    Constraint(
                        expr = bina[i] * (v - info[c.name][b][v.name][1]) <= 0)
                    )
                model.add_component(
                    'active_lower_of_'+v.name+'_for_'+b+'_wrt_'+c.name,
                    Constraint(
                        expr = bina[i] * (info[c.name][b][v.name][0] - v) <= 0)
                    )
                v.lb = min([l for l in info['bounds'][v.name] if type(l)!=str])
                v.ub = max([u for u in info['bounds'][v.name] if type(u)!=str])
            
            if c.ub != None:
                # add underestimation constraint
                model.add_component(
                    'underestimation_of_'+c.name+'_on_'+b,
                    Constraint(
                        expr = bina[i] * (quicksum(info[c.name][b]['weight'][v.name] * v for v in vars)\
                                          + info[c.name][b]['weight']['constant']\
                                              - info[c.name][b]['overest_error']) <= c.ub)
                    )
                
            # check if c is equality constraint
            if c.lb != None:
                # add overestimation constraint
                model.add_component(
                    'overestimaton_of_'+c.name+'_on_'+b,
                    Constraint(
                        expr = -bina[i] * (quicksum(info[c.name][b]['weight'][v.name] * v for v in vars)\
                                          + info[c.name][b]['weight']['constant']\
                                              + info[c.name][b]['underest_error']) <= -c.lb)
                    )
            
            i += 1
        
        c.deactivate()
    
    # catch nonlinear objectives
    nonlin_obj = [o for o in model.component_objects(Objective) if o.expr.polynomial_degree() != 1]
    for o in nonlin_obj:
        # catch variables appearing in objective
        vars = list(identify_variables(o.expr))
        
        # catch boxes for constraint and introduce binaries
        boxes = [b for b in info[o.name].keys() if 'box' in b]
        
        number_of_boxes = len(boxes)
        box_counter += number_of_boxes
        
        model.add_component(o.name+'_box_set', RangeSet(0,number_of_boxes-1))
        for s in model.component_objects(RangeSet):
            if s.name == o.name+'_box_set':
                model.add_component(o.name+'_box_binaries',
                                    Var(s, within=Binary))
        
        
        # define SOS1 constraint
        var_list = list(model.component_objects(Var))
        var_list.reverse()
        for bina in var_list:
            if bina.name == o.name+'_box_binaries':
                model.add_component(o.name+'_sos_cons',
                                    SOSConstraint(var=bina, sos=1))
                model.add_component(o.name+'_only_one_active',
                                    Constraint(expr=quicksum(bina[i] for i in
                                                     bina.index_set()) == 1))
                break
            
        # introduce relaxation for each box
        i = 0
        for b in boxes:
            # check if calculations for box need to be done
            if 'underest_error' not in info[o.name][b].keys():
                info[o.name][b] = calculate_box_info_objective_max(o, 
                                                               vars,
                                                               info[o.name][b],
                                                               call_model)
            
            # determine active partition and set variable bounds
            for v in vars:
                model.add_component(
                    'active_upper_of_'+v.name+'_for_'+b+'_wrt_'+o.name,
                    Constraint(
                        expr = bina[i] * (v - info[o.name][b][v.name][1]) <= 0)
                    )
                model.add_component(
                    'active_lower_of_'+v.name+'_for_'+b+'_wrt_'+o.name,
                    Constraint(
                        expr = bina[i] * (info[o.name][b][v.name][0] - v) <= 0)
                    )
                v.lb = min([l for l in info['bounds'][v.name] if type(l)!=str])
                v.ub = max([u for u in info['bounds'][v.name] if type(u)!=str])
            
            # add underestimation objective function
            if i == 0:
                model.add_component(
                    'overestimation_of_'+o.name,
                    Objective(
                        expr = bina[i] * (quicksum(info[o.name][b]['weight'][v.name] * v for v in vars)\
                                          + info[o.name][b]['weight']['constant']\
                                              + info[o.name][b]['underest_error']))
                    )
            else:
                for obj in model.component_objects(Objective):
                    if obj.name == 'overestimation_of_'+o.name:
                        obj.expr += bina[i] * (quicksum(info[o.name][b]['weight'][v.name] * v for v in vars)\
                                               + info[o.name][b]['weight']['constant']\
                                                   + info[o.name][b]['underest_error'])
                        break
            i += 1
        
        if not o.active:
            for obj in model.component_objects(Objective):
                if obj.name == 'overestimation_of_'+o.name:
                    obj.deactivate()
                    break
        
        model.del_component(o)
        model.add_component(o.name, Constraint(expr = o.expr <= 0))
        
        cons_list = list(model.component_objects(Constraint))
        cons_list.reverse()
        for c in cons_list:
            if c.name == o.name:
                c.deactivate()
        
    return model, info, box_counter
