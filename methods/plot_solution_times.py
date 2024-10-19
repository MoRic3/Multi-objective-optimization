#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 11:48:01 2024

@author: moritz
"""

import matplotlib.pyplot as plt
import numpy as np

def plot_solution_times(encl_dict, it):
    """
    routine or plottin the average solution times for MILP/NLP problems
    per iteration

    Parameters
    ----------
    encl_dict : dict
        containing all information collected by the algorithm.
    it : int
        representing the number of iterations needed by the algorithm.

    Returns
    -------
    None.

    """
    plt.figure()
    for i in np.arange(0,it):
        if i == 0:
            plt.semilogy(i, encl_dict[str(i)]['solution_time']/(encl_dict[str(i)]['problemcounter']+1e-10), 
                     'r^', alpha=0.5, label='Avg time for NLPs')
            plt.semilogy(i, encl_dict[str(i)]['relaxed_solution_time']/encl_dict[str(i)]['relaxedproblemcounter'],
                     'g^', alpha=0.5, label='Avg time MILPs')
            
        else:
            plt.semilogy(i, encl_dict[str(i)]['solution_time']/(encl_dict[str(i)]['problemcounter']+1e-10),
                     'r^', alpha = 0.5)
            plt.semilogy(i, encl_dict[str(i)]['relaxed_solution_time']/encl_dict[str(i)]['relaxedproblemcounter'],
                     'g^', alpha=0.5)

    plt.xlabel('iteration')
    plt.ylabel('time (s)')
    plt.title('solution time analysis analysis')
    plt.legend(loc='best')
    plt.show()        