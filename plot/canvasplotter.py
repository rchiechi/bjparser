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
import matplotlib.backends.tkagg as tkagg
from matplotlib.backends.backend_agg import FigureCanvasAgg
from tkinter import PhotoImage
from tmpfile import NamedTemporaryFile

def XYplot(master, canvas, X ,Y, labels={}):
    if not labels:
        labels={'title':'XY Plot',
                'X': 'distance',
                'Y': 'current'}
    fig = mpl.figure.Figure(figsize=(5, 4), dpi=80)
    ax = fig.add_subplot(111)
    #ax.plot(self.ivs_files[fileName]['d'], self.ivs_files[fileName]['I'])
    ax.plot(X,Y)
    fig.suptitle(labels['title'])
    figure_canvas_agg = FigureCanvasAgg(fig)
    figure_canvas_agg.draw()
    figure_x, figure_y, figure_w, figure_h = fig.bbox.bounds
    figure_w, figure_h = int(figure_w), int(figure_h)
    fig_photo = PhotoImage(master=master, width=figure_w, height=figure_h)
    canvas.create_image(figure_w/2, 
           figure_h/2, image=fig_photo)    
    # Unfortunately, there's no accessor for the pointer to the native renderer
    tkagg.blit(fig_photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)
    return fig_photo    

    