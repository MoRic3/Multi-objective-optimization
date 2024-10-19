#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 13:08:03 2024

@author: moritz
"""

import matplotlib.pyplot as plt

def plot_nondom(N, m, time, it, tol, width):
    """
    routine for plotting the epsilon-nondominated points found by the algorithm

    Parameters
    ----------
    N : list
        consisting of epsilon-nondominated points of the problem.
    m : int
        represnting the dimension of the image space.
    time : float
        representing the ellapsed time in s.
    it : int
        representing the iteration count.
    tol : float
        representing the width tolerance (epsilon).
    width : float
        representing the actually attained width.

    Returns
    -------
    None.

    """
    
    if m == 2:
        plt.figure()
        for solvec in N:
            plt.plot(solvec[0],solvec[1], 'gx')
        
        plt.xlabel(r'$f_1$')
        plt.ylabel(r'$f_2$')
        
    elif m == 3:
        plt.figure()
        ax = plt.axes(projection='3d')
        for solvec in N:
            ax.plot3D(solvec[0], solvec[1], solvec[2], 'gx')
            
        ax.set_xlabel(r'$f_1$')
        ax.set_ylabel(r'$f_2$')
        ax.set_zlabel(r'$f_3$')
        ax.view_init(elev=15, azim=-130)
        
    plt.title(r'$\epsilon$-nondominated points, tol: ' + str(tol) +
              ',' +'\n width: ' + str(round(width,3)) + ', time(s): '+
              str(round(time,1)) + ', iterations: ' + str(it))
    
    plt.show()