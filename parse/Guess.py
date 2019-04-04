#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 14:06:13 2019

@author: rchiechi
"""

#import os
import sys
#from parse.read import ReadIVS
#import logging
import threading
import queue

#import matplotlib as mpl
#mpl.use('TkAgg')
#import matplotlib.pyplot as plt # Without this there is not mpl.figure

#try:
##    import pandas as pd
##    from scipy.optimize import curve_fit,OptimizeWarning
##    import scipy.interpolate 
#    from scipy import interpolate
#    from scipy import stats
##    import scipy.misc 
##    import numpy as np
#    # SciPy throws a useless warning for noisy J/V traces
##    warnings.filterwarnings('ignore','.*Covariance of the parameters.*',OptimizeWarning)
#
#except ImportError as msg:
#    print("\n\t\t> > > Error importing module: %ss < < <s" % str(msg))
#    print("Try pip3 install <module>")
#    sys.exit()
#


class CountThread(threading.Thread):
    def __init__(self, alive, queue):
        threading.Thread.__init__(self)
        self.alive = alive
        self.queue = queue
        self.keep = []
        self.toss = []
        
    def run(self):
        while not self.queue.empty():
            if not self.alive.is_set():
                break
            try:
                job = self.queue.get()
            except queue.Empty:
                break
            n = CountPlateaux(job[1],job[2])
            if n < 10:
                self.toss.append(job[0])
            else:
                self.keep.append(job[0])

def CountPlateaux(X, Y):
    n = 0
    ymin, ymax = Y.min(), Y.max()
    Yrange = abs(ymax - ymin)
    for idx in range(5, len(Y)):
#        if abs(Y[idx] / ymax) < 0.1:
#            continue
#        if abs(Y[idx] / ymin) > 0.8:
#            continue
        _diff = abs(Y[idx-1] - Y[idx])
        if _diff:
            if _diff/Yrange > 0.05:
                n += 1            
    return n

