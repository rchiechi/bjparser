#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 08:52:13 2019

@author: rchiechi
"""

# import matplotlib.pyplot as plt # Without this there is not mpl.figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# from matplotlib.backends.backend_agg import FigureCanvasAgg
# from matplotlib.backend_bases import key_press_handler
# from mpl_toolkits.mplot3d import Axes3D # Needed for 3D plot axes types
# import scipy.signal
import numpy as np
import matplotlib as mpl
import gui.colors as cl

mpl.use('TkAgg')

for _key in ('up', 'down', 'left', 'right'):
    try:
        mpl.rcParams['keymap.back'].remove(_key)
    except ValueError:
        pass

__all__ = ['getXYplot', 'getHistplot']

#['Solarize_Light2', '_classic_test_patch', 'bmh', 'classic', 'dark_background', 
# 'fast', 'fivethirtyeight', 'ggplot', 'grayscale', 'seaborn', 'seaborn-bright',
#  'seaborn-colorblind', 'seaborn-dark', 'seaborn-dark-palette', 'seaborn-darkgrid',
#  'seaborn-deep', 'seaborn-muted', 'seaborn-notebook', 'seaborn-paper', 'seaborn-pastel',
#  'seaborn-poster', 'seaborn-talk', 'seaborn-ticks', 'seaborn-white', 'seaborn-whitegrid',
#  'tableau-colorblind10']

FCOLOR=cl.LIGHTBLUE
DPI=100

class FigureCanvas(FigureCanvasTkAgg):
    def destroy(self):
        self.get_tk_widget().destroy()

class NavigationToolbar(NavigationToolbar2Tk):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar2Tk.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom')]
    # def key_press_handler(self, event, canvas=None, toolbar=None):
    #     pass

def _getcanvas(fig, master):
    canvas = FigureCanvas(fig, master)  # A tk.DrawingArea.
    canvas.draw()
    toolbar = NavigationToolbar(canvas, master, pack_toolbar=False)
    toolbar.update()
    return canvas, toolbar

def getXYplot(master, X ,Y, labels=None):
    #https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html
    if labels is None:
        labels={'title':'XY Plot',
                'X': 'distance',
                'Y': 'current'}
    fig = mpl.figure.Figure(
                figsize=(5, 3.5),
                dpi=DPI,
                facecolor=FCOLOR,
                tight_layout=True)
    ax = fig.add_subplot(111)
    ax.plot(X,Y)
    ax.set_xlabel(labels['X'])
    ax.set_ylabel(labels['Y'])
    fig.suptitle(labels['title'])
    return _getcanvas(fig, master)

    
def getXYZplot(master, X, Y, labels=None):
    if labels is None:
        labels={'title':'XYZ Plot',
                'X': 'distance',
                'Y': 'current',
                'Z': 'trace'}
    fig = mpl.figure.Figure(
                figsize=(5, 3.5),
                dpi=80,
                facecolor=cl.LIGHTBLUE,
                tight_layout=True)
    
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel(labels['X'])
    ax.set_ylabel(labels['Y'])
    ax.set_zlabel(labels['Z'])
    for i, _x in enumerate(X):
        ax.plot(_x, Y[i], i, zdir='y')
    fig.suptitle(labels['title'])            

    return _getcanvas(fig, master)
        
def getHistplot(master, X, Y, Y_fit, labels=None): #pylint: disable=unused-argument
    if labels is None:
        labels={'title':'Histogram',
                'X':'G',
                'Y':'counts'}
        
    # Large arrays kill matplotlib
    if len(X)%2:
        X = X[:-1]
        Y = Y[:-1]
    while len(X) > 10000:
        newlen = int(len(X)/2)
        _x = X.reshape(-1,newlen)
        _y = Y.reshape(-1,newlen)
        X = _x.reshape(-1,newlen).mean(axis=1)
        Y = _y.reshape(-1,newlen).mean(axis=1)
        
    Y = np.log10(Y)
    fig = mpl.figure.Figure(
        figsize=(5, 3.5),
        dpi=DPI,
        facecolor=FCOLOR,
        tight_layout=True)
    ax = fig.add_subplot(111)
    ax.bar(X, Y, width=0.000005, align='center', color='r')
    ax.set_xlabel(labels['X'])
    ax.set_ylabel('Log '+labels['Y'])
    fig.suptitle(labels['title'])            
    return _getcanvas(fig, master)




def getHistplot2d(master, X, Y, Y_fit, labels=None): #pylint: disable=unused-argument
    if labels is None:
        labels={'title':'Histogram',
                'X':'G',
                'Y':'counts'}
        
    # Large arrays kill matplotlib
    if len(X)%2:
        X = X[:-1]
        Y = Y[:-1]
    while len(X) > 10000:
        newlen = int(len(X)/2)
        _x = X.reshape(-1,newlen)
        _y = Y.reshape(-1,newlen)
        X = _x.reshape(-1,newlen).mean(axis=1)
        Y = _y.reshape(-1,newlen).mean(axis=1)

    Y = np.log10(Y)
    fig = mpl.figure.Figure(
        figsize=(5, 3.5),
        dpi=DPI,
        facecolor=FCOLOR)
    ax = fig.add_subplot(111)
    ax.bar(X, Y, width=0.000005, align='center', color='r')
    ax.set_xlabel(labels['X'])
    ax.set_ylabel('Log '+labels['Y'])
    fig.suptitle(labels['title'])       
    return _getcanvas(fig, master)
            
        