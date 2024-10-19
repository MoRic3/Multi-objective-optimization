#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 13:53:41 2024

@author: moritz
"""

import numpy as np
import sys

def update_nondom(N, y):
    """
    update the stable set of potentially nondominated points w.r.t. a new
    potentially nondominated point

    for reference see Algorithm 3 in

    Link, M. and Volkwein, S.
    Adaptive piecewise linear relaxations for enclosure computations for
    nonconvex multi-objective mixed-integer quadratically constrained programs
    J. Global Optim. 87. 2023.

    Parameters
    ----------
    N : list
        consisting of a stable set of potentially nondominated points.
    y : array
        the new potentially nondominated point.

    Returns
    -------
    new_N : list
        updated list of potentially nondominated points.
    check : boolean
        indicating if y belongs to updated list of potentially nondominated
        points, i.e., if y improved N.

    """

    # check if N is non-empty
    if len(N) == 0:
        new_N = [y]
        check = 1
        return new_N, check

    else:
        # initialize new list of potentially nondominated points
        new_N = []

        # go through points
        check = 1
        for x in N:
            # check shapes
            if np.shape(x) != np.shape(y):
                print('update of potentially nondominated points not possible:\
                      shapes do not align')
                sys.exit(1)

            # check if y already belongs to N
            if (y == x).all():
                new_N = N
                check = 0
                return new_N, check

            # check if x dominates y
            elif (x <= y).all():
                new_N.append(x)
                check = 0

            # check if x is not weakly dominated by y
            elif (x < y).any():
                new_N.append(x)

        # check if y is dominated by N
        if check == 1:
            new_N.append(y)

    return new_N, check
