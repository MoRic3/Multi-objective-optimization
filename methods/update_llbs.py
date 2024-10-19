#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 10:46:01 2024

@author: moritz
"""

import copy as cp
import numpy as np
import sys

def update_llbs(llbs, defpois, z):
    """
    routine for updating set of local lower bounds with corresponding defining
    points w.r.t. a new point z

    Adapted version for local lower bounds of Algorithm 5 in

    Klamroth, K. and Lacour, R. and Vanderpooten, D.
    On the representation of the search region in multi-objective optimization.
    Eur. J. Oper. Res. 245(3). 2015.

    Parameters
    ----------
    llbs : list
        representing the current assignment of local lower bounds.
    defpois : dict
        with llbs as keys in first layer and indices as keys in second layer
        and list of defining points as values in third layer.
    z : array
        representing the update point.

    Returns
    -------
    new_llbs : list
                representing the updated assignment of local lower bounds.
    new_defpois : dict
                representing the updated assignment of defining points.

    """

    # save original defpoi list
    defpois_old = cp.deepcopy(defpois)

    # catch dimension of vectors
    n = len(z)

    # determine list of affected llbs
    A = [llb for llb in llbs if (llb<z).all()]

    # update defining point stes if necessary
    for llb in llbs:
        # check shapes
        if np.shape(llb) != np.shape(z):
            print('update of llbs not possible: shapes do not align')
            sys.exit(1)

        for j in np.arange(0,n):
            if z[j] == llb[j] and (np.delete(llb,j) < np.delete(z,j)).all():
                defpois[str(llb)][j].append(z)

    # big loop
    # introduce new set
    P = []

    for llb in A:
        for j in np.arange(0,n):
            zmaxlist = []
            for k in np.arange(0,n):
                if k != j:
                    for i in np.arange(0, len(defpois_old[str(llb)][k])):
                        if i == 0:
                            zmax = defpois_old[str(llb)][k][i][j]
                        else:
                            zmax = max(zmax, defpois_old[str(llb)][k][i][j])
                    zmaxlist.append(zmax)

            zmin = min(zmaxlist)

            if z[j] < zmin:
                lj = cp.deepcopy(llb)
                lj[j] = cp.copy(z[j])
                P.append(lj)
                defpois[str(lj)] = {}
                defpois[str(lj)][j] = [z]
                for k in np.arange(0,n):
                    if k != j:
                        defpois[str(lj)][k] = []
                        for i in np.arange(0,len(defpois_old[str(llb)][k])):
                            if z[j] < defpois_old[str(llb)][k][i][j]:
                                new_defpoi = cp.deepcopy(defpois_old[str(llb)][k][i])
                                defpois[str(lj)][k].append(new_defpoi)

    # build new list of llbs
    new_llbs = P
    for llb in llbs:
        add = True
        for a in A:
            if (llb == a).all():
                add = False
                break
        for llb_check in new_llbs:
            if (llb == llb_check).all():
                add = False
                break
        if add:
            new_llbs.append(llb)

    # build new dict of defpois
    new_defpois = {}
    for llb in new_llbs:
        new_defpois[str(llb)] = cp.deepcopy(defpois[str(llb)])

    return new_llbs, new_defpois
