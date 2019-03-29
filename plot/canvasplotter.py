#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 08:52:13 2019

@author: rchiechi
"""

__all__ = ['XYplot']

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
        for i in range(0, len(X)):
            print(X[i])
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