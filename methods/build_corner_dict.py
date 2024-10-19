#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 10:36:31 2024

@author: moritz
"""

import numpy as np

def generate_corner_points(info, i=0):
    
    vars = list(info.keys())
    if i == len(vars):
        return [{}]
    lower, upper = info[vars[i]][0], info[vars[i]][1]
    points = []
    for point in generate_corner_points(info, i+1):
        points.append({**point, vars[i]: lower})
        points.append({**point, vars[i]: upper})
    return points

def generate_corner_dict(info):
    
    
    corner_points = generate_corner_points(info)
    corner_dict = {}
    for i in np.arange(0, len(corner_points)):
        corner_dict[i] = corner_points[i]
    return corner_dict