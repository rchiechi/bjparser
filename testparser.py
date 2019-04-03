#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 14:06:13 2019

@author: rchiechi
"""

import os
import sys
from parse.read import ReadIVS
import logging
import threading

import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt # Without this there is not mpl.figure

try:
#    import pandas as pd
#    from scipy.optimize import curve_fit,OptimizeWarning
    import scipy.interpolate 
    from scipy import stats
#    import scipy.misc 
#    import numpy as np
    # SciPy throws a useless warning for noisy J/V traces
#    warnings.filterwarnings('ignore','.*Covariance of the parameters.*',OptimizeWarning)

except ImportError as msg:
    print("\n\t\t> > > Error importing module: %ss < < <s" % str(msg))
    print("Try pip3 install <module>")
    sys.exit()
#
FN="/Volumes/Data/rchiechi/Desktop/STMBJ/TEST/PA027.ivs"
#FN="/Volumes/Data/rchiechi/Desktop/STMBJ/TEST/PA005.ivs"
#FN="/Volumes/Data/rchiechi/Desktop/STMBJ/TEST/PA028.ivs"
#FN="/Volumes/Data/rchiechi/Desktop/STMBJ/TEST/PA134.ivs"



#def CountPlateaux(X, Y):
    

logger = logging.getLogger('testparer')
lock = threading.RLock()
ivs = ReadIVS(logger, lock, opts={})
ivs.AddFile(FN)

spl = scipy.interpolate.UnivariateSpline(
        ivs.frames[FN]['d'],ivs.frames[FN]['I'], k=5, s=0.1)
#spl = scipy.interpolate.CubicSpline(
#        ivs.frames[FN]['d'],ivs.frames[FN]['I'])

spld = spl.derivative(1)
n = 0
s = spld(ivs.frames[FN]['d'][0])
for d in ivs.frames[FN]['d']:
    if spld(d) * s < 0:
        n += 1
    s = spld(d)
    
print(n)

n = 0
x, y = [], []
slope, intercept, r_value, p_value, std_err = stats.linregress(ivs.frames[FN]['d'], ivs.frames[FN]['I'])
print('slope: %s' % slope)
print('r^2: %s' % r_value**2)

i = 0
for d in ivs.frames[FN]['d']:
    x.append(d)
    y.append(spl(d))
    i += 1
    if i < 5:
        continue
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    i = 0
#    print(slope)
    if not r_value:
        continue
    if r_value**2 < 0.9:
        n += 1
        x, y = [], []
#    print(slope)
#    print(r_value**2)

print(n)

x = ivs.frames[FN]['d']
y = [spl(x) for x in ivs.frames[FN]['d']]
plt.plot(ivs.frames[FN]['d'], ivs.frames[FN]['I'])
plt.plot(x,y)
plt.show()


