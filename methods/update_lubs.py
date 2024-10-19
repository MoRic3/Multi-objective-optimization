#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 11:50:00 2024

@author: moritz
"""

import copy as cp
import numpy as np
import sys

def update_lubs(lubs, defpois, z):
    """
    routine for updating set of local upper bounds with corresponding defining
    points w.r.t. a new point z
    
    for reference see Algorithm 5 in
    
    Klamroth, K. and Lacour, R. and Vanderpooten, D.
    On the representation of the search region in multi-objective optimization.
    Eur. J. Oper. Res. 245(3). 2015.

    Parameters
    ----------
    lubs : list
        representing the current assignment of local upper bounds.
    defpois : dict
        with lubs as keys in first layer and indices as keys in second layer
        and list of defining points as values in third layer.
    z : array
        representing the update point.

    Returns
    -------
    new_lubs : list
        representing the updated assignment of local upper bounds.
    new_defpois : dict
        representing the updated assignment of defining points.

    """
    
    # save original defpoi list
    defpois_old = cp.deepcopy(defpois)
    
    # catch dimension of vectors
    n = len(z)
    
    # determine list of affected lubs
    A = [lub for lub in lubs if (z<lub).all()]
    
    # update defining point sets if necessary
    for lub in lubs:
        # check shapes
        if np.shape(lub) != np.shape(z):
            print('update of lubs not possible: shapes do not align')
            sys.exit(1)
        
        for j in np.arange(0,n):
            if z[j] == lub[j] and (np.delete(z,j) < np.delete(lub,j)).all():
                defpois[str(lub)][j].append(z)
    
    # big loop
    # introduce new set
    P = []
    
    for lub in A:
        for j in np.arange(0,n):
            zminlist = []
            for k in np.arange(0,n):
                if k != j:
                    for i in np.arange(0,len(defpois_old[str(lub)][k])):
                        if i == 0:
                            zmin = defpois_old[str(lub)][k][i][j]
                        else:
                            zmin = min(zmin, defpois_old[str(lub)][k][i][j])
                    zminlist.append(zmin)
            
            zmax = max(zminlist)
            
            if zmax < z[j]:
                uj = cp.deepcopy(lub)
                uj[j] = cp.copy(z[j])
                P.append(uj)
                defpois[str(uj)] = {}
                defpois[str(uj)][j] = [z]
                for k in np.arange(0,n):
                    if k != j:
                        defpois[str(uj)][k] = []
                        for i in np.arange(0,len(defpois_old[str(lub)][k])):
                            if defpois_old[str(lub)][k][i][j] < z[j]:
                                new_defpoi = cp.deepcopy(defpois_old[str(lub)][k][i])
                                defpois[str(uj)][k].append(new_defpoi)
    
    # build new list of lubs
    new_lubs = P
    for lub in lubs:
        add = True
        for a in A:
            if (lub == a).all():
                add = False
                break
        for lub_check in new_lubs:
            if (lub == lub_check).all():
                add = False
                break
        if add:
            new_lubs.append(lub)
    
    # build new dict of defpois
    new_defpois = {}
    for lub in new_lubs:
        new_defpois[str(lub)] = cp.deepcopy(defpois[str(lub)])
    
    return new_lubs, new_defpois