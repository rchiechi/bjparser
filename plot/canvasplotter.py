#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 08:52:13 2019

@author: rchiechi
"""

__all__ = ['XYplot']

import numpy as np
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt # Without this there is not mpl.figure
from mpl_toolkits.mplot3d import Axes3D # Needed for 3D plot axes types
import matplotlib.backends.tkagg as tkagg
from matplotlib.backends.backend_agg import FigureCanvasAgg

class XYplot:
    #https://matplotlib.org/gallery/user_interfaces/embedding_in_tk_canvas_sgskip.html
    def __init__(self, X ,Y, labels={}):
        if not labels:
            labels={'title':'XY Plot',
                    'X': 'distance',
                    'Y': 'current'}
        fig = mpl.figure.Figure(figsize=(5, 3.5), dpi=80)
        ax = fig.add_subplot(111)
        ax.plot(X,Y)
        ax.set_xlabel(labels['X'])
        ax.set_ylabel(labels['X'])
        fig.suptitle(labels['title'])
        self.figure_canvas_agg = FigureCanvasAgg(fig)
        self.figure_canvas_agg.draw()
        figure_x, figure_y, figure_w, figure_h = fig.bbox.bounds
        self.figure_w, self.figure_h = int(figure_w), int(figure_h)
    def Draw(self, fig_photo):  
        # Unfortunately, there's no accessor for the pointer to the native renderer
        self.fig_photo = fig_photo
        tkagg.blit(self.fig_photo, self.figure_canvas_agg.get_renderer()._renderer, colormode=2)

    
class XYZplot:
    #https://matplotlib.org/gallery/user_interfaces/embedding_in_tk_canvas_sgskip.html
    def __init__(self, X, Y, labels={}):
        if not labels:
            labels={'title':'XYZ Plot',
                    'X': 'distance',
                    'Y': 'current',
                    'Z': 'trace'}
        fig = mpl.figure.Figure(figsize=(5, 3.5), dpi=80)
        
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlabel(labels['X'])
        ax.set_ylabel(labels['Y'])
        ax.set_zlabel(labels['Z'])
        for i in range(0, len(X)):
            ax.plot(X[i], Y[i], i, zdir='y')
        fig.suptitle(labels['title'])            
        self.figure_canvas_agg = FigureCanvasAgg(fig)
        self.figure_canvas_agg.draw()
        figure_x, figure_y, figure_w, figure_h = fig.bbox.bounds
        self.figure_w, self.figure_h = int(figure_w), int(figure_h)

    def Draw(self, fig_photo):  
        # Unfortunately, there's no accessor for the pointer to the native renderer
        self.fig_photo = fig_photo
        tkagg.blit(self.fig_photo, self.figure_canvas_agg.get_renderer()._renderer, colormode=2)
        
class Histplot:
    
    def __init__(self, X, Y, Y_fit, labels={}):
        if not labels:
            labels={'title':'Histogram',
                    'X':'G',
                    'Y':'counts'}
        fig = mpl.figure.Figure(figsize=(5, 3.5), dpi=80)
        
        ax = fig.add_subplot(111)
        ax.plot(X, Y_fit, lw=2.0, color='b', label='Fit')
#        ax.bar(X, Y, width=0.1, color='r')

        ax.set_xlabel(labels['X'])
        ax.set_ylabel(labels['Y'])

        fig.suptitle(labels['title'])            
        self.figure_canvas_agg = FigureCanvasAgg(fig)
        self.figure_canvas_agg.draw()
        figure_x, figure_y, figure_w, figure_h = fig.bbox.bounds
        self.figure_w, self.figure_h = int(figure_w), int(figure_h)

    def Draw(self, fig_photo):  
        # Unfortunately, there's no accessor for the pointer to the native renderer
        self.fig_photo = fig_photo
        tkagg.blit(self.fig_photo, self.figure_canvas_agg.get_renderer()._renderer, colormode=2)
            
    
#    def __init__(self, G, lables={}):
#        if not lables:
#            labels={'title':'Histogram',
#                    'X':'G',
#                    'Y':'counts'}
#        
#        #X = X/G = [i*(1e-9)/0.1/0.0000775 for i in current]
#        n, bins, patches = plt.hist(G, 100, density=True, facecolor='g', alpha=0.75)
#        plt.xlabel(labels['X'], fontsize=14)
#        plt.ylabel(labels['Y'], fontsize=14)
#        plt.title(labels['title'])
#        
#    def show(self):
#        plt.gca()
        plt.show()

#        fig = plt.figure(figsize=(16,10))
#        ax = fig.add_subplot(111)
# the histogram of the data
#n, bins, patches = plt.hist(x, 50, density=True, facecolor='g', alpha=0.75)
#
#
#plt.xlabel('Smarts')
#plt.ylabel('Probability')
#plt.title('Histogram of IQ')
#plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
#plt.axis([40, 160, 0, 0.03])
#plt.grid(True)
#plt.show()
            
            
        