#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 18:55:30 2024

@author: moritz
"""

import matplotlib.pyplot as plt
import numpy as np

def plot_search_zone_count(encl_dict, it):
    """
    routine for plotting the number of search visited resp enforcedly improved
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
    first_OBBT = True
    
    plt.figure()
    for i in np.arange(0,it):
        if i == 0:
            plt.plot(i, encl_dict[str(i)]['# of search zones'], 
                     'r^', alpha=0.5, label='# of search zones visited')
            plt.plot(i, encl_dict[str(i)]['# of search zones closed'],
                     'y^', alpha=0.5, label='# of search zones closed')
            plt.plot(i, encl_dict[str(i)]['# of enforced feasibility check'],
                     'g^', alpha=0.5, label='# of search zones improved enforcedly')
            plt.plot(i, encl_dict[str(i)]['# of considered feasible'],
                     'b^', alpha=0.5, label='# of search zones improved by feas-dec')
            
            
        else:
            plt.plot(i, encl_dict[str(i)]['# of search zones'],
                     'r^', alpha = 0.5)
            plt.plot(i, encl_dict[str(i)]['# of search zones closed'],
                     'y^', alpha=0.5)
            plt.plot(i, encl_dict[str(i)]['# of enforced feasibility check'],
                     'g^', alpha=0.5)
            plt.plot(i, encl_dict[str(i)]['# of considered feasible'],
                     'b^', alpha=0.5)
            
    plt.xlabel('iteration')
    plt.ylabel('# of problems')
    plt.title('number of search zones visited and improved enforcedly per iteration')
    plt.legend(loc='best')
    plt.show()  