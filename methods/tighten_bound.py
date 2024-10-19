#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 11:00:34 2024

@author: moritz
"""

from pyomo.environ import *

from relax_model import *
from rounding_routines import *


def tighten_bound(call_model, var, ind, u, info, solution, options):
    """
    routine for tightening the lower/upper -- indicated by 'ind' -- variable
    bound of 'var' using the objective cut-offs of the local upper bound 'u'
    and the optimal values of 'solution' as warm star

    INSERT TIME LIMIT!!!!!!

    Parameters
    ----------
    call_model : function
        returning a pyomo model of the problem to be solved.
    var : str
        representing the variable name which is to be tightened.
    ind : str
        determining if the lower or the upper bound of the variable should be
        tightened.
    u : ndarray
        representing the current objective cut-offs.
    info : dict
        containing all information for setting up the current piecewise linear
        relaxation of the model of interest.
    solution : dict
        with variable names as keys and corresponding optimal values as values.
    options : structure
        containing all optional settings for the algorithm.

    Returns
    -------
    new_bound : float
        representing the possibly tightened bound.
    sol_time : float
        representing the solution time of the problem.

    """

    # catch options
    try:
        milp_solver = options.milp_solver
    except:
        milp_solver = 'gurobi'

    try:
        OBBT_timelimit = options.OBBT_timelimit
    except:
        OBBT_timelimit = False

    try:
        OBBT_gap = options.OBBT_gap
    except:
        OBBT_gap = False

    # set up relaxed model
    model = call_model(0)
    model, info, box_counter = relax_model(model, call_model, info)

    # introduce upper bounds on objectives
    for i in np.arange(0,len(u)):
        for o in model.component_objects(Objective):
            if 'objective'+str(i) in o.name:
                model.add_component('upper_bound_on_'+str(i)+'-th_objective',
                                    Constraint(expr = o.expr - u[i] <= 0))
                o.deactivate()

    # determine new objective function and set warm starts
    for v in model.component_objects(Var):
        if v.is_indexed():
            for i in v.index_set():
                if v[i].name == var:
                    if ind == 'lower':
                        model.new_bound = Objective(expr = v[i])
                        old_bound = v[i].lb
                    elif ind == 'upper':
                        model.new_bound = Objective(expr = v[i],
                                                      sense=maximize)
                        old_bound = v[i].ub
                # set warm starts
                v[i] = solution[v[i].name]
        else:
            if v.name == var:
                if ind == 'lower':
                    model.new_bound = Objective(expr = v)
                    old_bound = v.lb
                elif ind == 'upper':
                    model.new_bound = Objective(expr = v,
                                                  sense=maximize)
                    old_bound = v.ub
            # set warm starts
            v = solution[v.name]

    # solve model
    opt = SolverFactory(milp_solver)

    if milp_solver == 'gurobi':
        if OBBT_timelimit:
            opt.options['TimeLimit'] = OBBT_timelimit
        if OBBT_gap:
            opt.options['MIPGap'] = OBBT_gap
    elif milp_solver == 'scip':
        if OBBT_timelimit:
            opt.options['limits/time'] = OBBT_timelimit
        if OBBT_gap:
            opt.options['limits/gap'] = OBBT_gap

    results = opt.solve(model, tee=False, warmstart=True, load_solutions=False)

    try:
        sol_time = results.solver.time
    except:
        sol_time = OBBT_timelimit

    # catch new bound
    if ind == 'lower':
        new_bound = results.problem.lower_bound
    else:
        new_bound = results.problem.upper_bound

    if type(new_bound) == str:
        return old_bound, sol_time

    # round bound
    if ind == 'lower':
        new_bound = rounding_lower(new_bound, 4)
    else:
        new_bound = rounding_upper(new_bound, 4)

    return new_bound, sol_time
