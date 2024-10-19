#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 10:56:36 2024

@author: moritz
"""

import matplotlib.pyplot as plt
import numpy as np

def plot_preimage_information(encl_dict, it):
    """
    routine for plotting the average resp. maximal preimage set boxes per
    iteration    

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
            plt.plot(i, encl_dict[str(i)]['maxpreimageboxes'], 'r^', 
                     alpha=0.5, label='Max PSB')
            plt.plot(i, encl_dict[str(i)]['preimageboxcounter']/encl_dict[str(i)]['relaxedproblemcounter'],
                     'g^', alpha=0.5, label='Avg PSB')
            
        else:
            plt.plot(i, encl_dict[str(i)]['maxpreimageboxes'], 'r^', alpha = 0.5)
            plt.plot(i, encl_dict[str(i)]['preimageboxcounter']/encl_dict[str(i)]['relaxedproblemcounter'],
                     'g^', alpha=0.5)

    plt.xlabel('iteration')
    plt.ylabel('# of boxes')
    plt.title('preimage set boxes analysis')
    plt.legend(loc='best')
    plt.show()            
    