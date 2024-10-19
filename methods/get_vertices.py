#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 11:26:29 2024

@author: moritz
"""

import numpy as np

def get_vertices(llb, lub):
    """
    routine that generates vertices for the 3-dim box defined by llb and lub

    Parameters
    ----------
    llb : array
        representing the lower corner of the box.
    lub : array
        representing the upper corner of the box.

    Returns
    -------
    vtx : list
        consisting of the vertices of the 3-dim box.

    """
    # vertex data
    vtx0 = np.array([
        [llb[0], llb[1], llb[2]],
        [llb[0], lub[1], llb[2]],
        [llb[0], lub[1], lub[2]],
        [llb[0], llb[1], lub[2]],
        ])
    
    vtx1 = np.array([
        [lub[0], llb[1], llb[2]],
        [lub[0], lub[1], llb[2]],
        [lub[0], lub[1], lub[2]],
        [lub[0], llb[1], lub[2]],
        ])
    
    vtx2 = np.array([
        [llb[0], llb[1], llb[2]],
        [llb[0], lub[1], llb[2]],
        [lub[0], lub[1], llb[2]],
        [lub[0], llb[1], llb[2]],
        ])
    
    vtx3 = np.array([
        [llb[0], llb[1], lub[2]],
        [llb[0], lub[1], lub[2]],
        [lub[0], lub[1], lub[2]],
        [lub[0], llb[1], lub[2]],
        ])
    
    vtx4 = np.array([
        [llb[0], llb[1], llb[2]],
        [lub[0], llb[1], llb[2]],
        [lub[0], llb[1], lub[2]],
        [llb[0], llb[1], lub[2]],
        ])
    
    vtx5 = np.array([
        [llb[0], lub[1], llb[2]],
        [lub[0], lub[1], llb[2]],
        [lub[0], lub[1], lub[2]],
        [llb[0], lub[1], lub[2]],
        ])
    
    vtx = [vtx0, vtx1, vtx2, vtx3, vtx4, vtx5]
    
    return vtx