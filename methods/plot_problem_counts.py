#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 12:03:32 2024

@author: moritz
"""

import matplotlib.pyplot as plt
import numpy as np

def plot_problem_counts(encl_dict, it):
    """
    routine for plotting the number of MILP/NLP/OBBT problems to be
    solved per iteration

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
    first_OBBT = True
    
    plt.figure()
    for i in np.arange(0,it):
        if i == 0:
            plt.plot(i, encl_dict[str(i)]['problemcounter'], 
                     'r^', alpha=0.5, label='# of NLPs')
            plt.plot(i, encl_dict[str(i)]['relaxedproblemcounter'],
                     'g^', alpha=0.5, label='# of MILPs')
            
        else:
            plt.plot(i, encl_dict[str(i)]['problemcounter'],
                     'r^', alpha = 0.5)
            plt.plot(i, encl_dict[str(i)]['relaxedproblemcounter'],
                     'g^', alpha=0.5)

        if encl_dict[str(i)]['# of OBBT MILPs'] > 0:
            if first_OBBT:
                plt.plot(i, encl_dict[str(i)]['# of OBBT MILPs'],
                         'b^', alpha=0.5, label='# of OBBT MILPs')
                first_OBBT = False
            else:
                plt.plot(i, encl_dict[str(i)]['# of OBBT MILPs'],
                         'b^', alpha=0.5)
                
    plt.xlabel('iteration')
    plt.ylabel('# of problems')
    plt.title('number of problems solved per iteration')
    plt.legend(loc='best')
    plt.show()  