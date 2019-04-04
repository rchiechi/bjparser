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
#FN="/Volumes/Data/rchiechi/Desktop/STMBJ/TEST/PA027.ivs"
#FN="/Volumes/Data/rchiechi/Desktop/STMBJ/TEST/PA005.ivs"

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
#    slope, intercept, r_value, p_value, std_err = stats.linregress(X, Y)
#    if abs(slope) < 0.1:
#        return n
    Yrange = abs(Y.max() - Y.min())
#    spl = interpolate.UnivariateSpline(
#        X, Y, k=5, s=X[-1]/100000)

#    x,y = [], []
#    i = 0
#    for _x in X:
#        x.append(_x)
#        y.append(spl(_x))
#        i += 1
#        if i < 5:
#            continue
    for idx in range(1, len(Y)):
        _diff = abs(Y[idx-1] - Y[idx])
        if _diff:
            if (_diff/Yrange)*100 > 10:
                n += 1            
#        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
#        i = 0
#        if not r_value:
#            continue
#        if r_value**2 < 0.9:
##            n += 1
#            x, y = [], []
    return n

