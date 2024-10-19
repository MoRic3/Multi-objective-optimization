#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 11:18:52 2024

@author: moritz
"""


import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as a3
import numpy as np

from get_vertices import *

def plot_enclosure(encl_dict, m, time, it, tol, width):
    """
    routine for plotting the enclosure of the problem

    Parameters
    ----------
    encl_dict : dict
        containing all information collected by the algorithm.
    m : int
        determining the dimension of the image space.
    time : float
        representing the time needed by the algorithm.
    it : int
        representing the number of iterations needed by the algorithm.
    tol : float
        representing the width termination tolerance.
    width : float
        representing the .

    Returns
    -------
    None.

    """
    lubs = encl_dict['lubs']
    llbs = encl_dict['llbs']
    zl = encl_dict['zl']
    zu = encl_dict['zu']    

    if m == 2:
        plt.figure()
        
        for lub in lubs:
            for llb in llbs:
                if (llb < lub).all():
                    x = np.zeros(4)
                    y = np.zeros(4)
                    
                    x[0] = llb[0]
                    y[0] = lub[1]
                    
                    x[1] = llb[0]
                    y[1] = llb[1]
                    
                    x[2] = lub[0]
                    y[2] = llb[1]
                    
                    x[3] = lub[0]
                    y[3] = lub[1]
                    
                    plt.fill(x,y,'b',alpha=0.2)
        
        plt.xlabel(r'$f_1$')
        plt.ylabel(r'$f_2$')
    
    elif m == 3:
        fig = plt.figure()
        ax = plt.axes(projection='3d')

        for lub in lubs:
            for llb in llbs:
                if (llb <= lub).all():
                    vtx = get_vertices(llb,lub)
                    tri = a3.art3d.Poly3DCollection(vtx, alpha=0.2)
                    tri.set_edgecolor('k')

                    ax.add_collection3d(tri)

        ax.set(xlim=(zl[0], zu[0]), ylim=(zl[1], zu[1]), zlim=(zl[2], zu[2]))
        ax.set(xlabel=r'$f_1$', ylabel=r'$f_2$', zlabel=r'$f_3$')
        ax.view_init(elev=15, azim=-130)

    plt.title('enclosure, tol: ' + str(tol) +
              ',' +'\n width: ' + str(round(width,3)) + ', time(s): '+
              str(round(time,1)) + ', iterations: ' + str(it))    

    plt.show()