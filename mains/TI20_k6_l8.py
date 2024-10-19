#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 12:29:42 2024

@author: moritz
"""

from pyomo.environ import *
from pyomo.core.expr.current import identify_variables

import sys

sys.path.append('../methods')

from compute_enclosure import *

"""
problem instance (P3) with k=6 and n=8 from
Eichfelder, G., Stein, O., and Warnow, L. A Solver For Multiobjective
Mixed-Integer Convex and Nonconvex Optimization. 2023

"""

import cProfile

plt.close('all')

class structure():
    pass


# define the model
def build_model(m):

    model = ConcreteModel()

    # define variables
    model.x1 = Var(within=Reals, bounds=(0,1))
    model.x2 = Var(within=Reals, bounds=(0,1))
    model.x3 = Var(within=Reals, bounds=(0,1))
    model.x4 = Var(within=Reals, bounds=(0,1))
    model.x5 = Var(within=Reals, bounds=(0,1))
    model.x6 = Var(within=Reals, bounds=(0,1))

    model.x7 = Var(within=Integers, bounds=(-3,3))
    model.x8 = Var(within=Integers, bounds=(-3,3))
    model.x9 = Var(within=Integers, bounds=(-3,3))
    model.x10 = Var(within=Integers, bounds=(-3,3))
    model.x11 = Var(within=Integers, bounds=(-3,3))
    model.x12 = Var(within=Integers, bounds=(-3,3))
    model.x13 = Var(within=Integers, bounds=(-3,3))
    model.x14 = Var(within=Integers, bounds=(-3,3))

    # define constraints
    model.cons0 = Constraint(expr = -model.x1**2 - model.x2**2 - model.x3**2\
				  - model.x4**2 - model.x5**2 - model.x6**2\
				  + 1 <= 0)
    model.cons1 = Constraint(expr = model.x7**2 + model.x8**2 + model.x9**2 \
    				  + model.x10**2 + model.x11**2 + model.x12**2 \
                                  + model.x13**2 + model.x14**2 - 9 <= 0)

    # define objectives
    model.objective0 = Objective(expr = model.x1 + model.x2 + model.x3 \
				      + model.x7 + model.x8 + model.x9 \
                                      + model.x10)
    model.objective1 = Objective(expr = model.x4 + model.x5 + model.x6 \
                                      + model.x11 + model.x12 + model.x13 \
                                      + model.x14)

    for o in model.component_objects(Objective):
        if not 'objective'+str(m) in o.name:
            o.deactivate()

    return model

# set up the parameters
parameter = structure()
parameter.m = 2
parameter.tol = 0.1
parameter.maxiter = 1000
parameter.timeout = 3600
parameter.factor_delta = 0.95 * parameter.tol

# set up options
options = structure()
options.solve_direct = False
options.show_plots = True
options.gap_tolerance = 1e-4
options.nlp_feasibility_only = False
options.constraint_tolerance = 1e-2
options.adaptive_refinement = True
options.bound_tightening = 3
# options.var_count_OBBT = 0.5

options.soft_utopian_check = True
options.tight_image_box = False
options.refine_until_feasible_search = 30
options.enforced_BT = True

encl_dict, it = compute_enclosure(build_model, parameter, options)
