#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 13:18:21 2019

@author: rchiechi
"""
import os
import logging
import platform
import math
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.backends.tkagg as tkagg
from matplotlib.backends.backend_agg import FigureCanvasAgg
import gui.colors as cl
import gui.tooltip as tip
from util.Cache import Cache
from util.logger import GUIHandler


class BJParserFrame(tk.Frame):

    indir=str()
    outdir=str()
    selected_files = []
    in_files = []
    
    def __init__(self, opts, master=None):
        tk.Frame.__init__(self, master)
        self.boolmap = {1:True, 0:False}
        try:
            self.last_input_path = os.getcwd()
        except KeyError:
            self.last_input_path = os.path.expanduser('~')
        self.opts = opts        
        self.master.tk_setPalette(background=cl.GREY,
            activeBackground=cl.GREY)
        self.master.title("RCCLab STMBJ Data Parser")
        self.master.geometry('900x850+250-250')
        self.pack(fill=tk.BOTH)
        self.__createWidgets()
        self.cache = Cache(self.logger)
        self.ToFront()
        self.mainloop()
        
        
    def __createWidgets(self):
            
        self.ButtonFrame = ttk.Frame(self)
        self.LoggingFrame = ttk.Frame(self)
        self.FileListBoxFrame = ttk.Frame(self)
    
        yScroll = ttk.Scrollbar(self.LoggingFrame, orient=tk.VERTICAL)
        self.Logging = tk.Text(self.LoggingFrame, height=20, width=0,  
                bg=cl.BLACK, fg=cl.WHITE, yscrollcommand=yScroll.set)
        yScroll['command'] = self.Logging.yview
        self.Logging.pack(side=tk.LEFT,fill=tk.BOTH,expand=True)
        yScroll.pack(side=tk.RIGHT,fill=tk.Y)

        self.__createButtons()
        self.__createFileListBox()
#        self.__createOptions()

        self.ButtonFrame.pack(side=tk.BOTTOM,fill=None)
        self.FileListBoxFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.LoggingFrame.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.logger = logging.getLogger('parser.gui')
        self.handler = GUIHandler(self.Logging)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(getattr(logging,self.opts.loglevel.upper()))
        self.logger.info("Logging...")
        self.handler.flush()
        self.updateFileListBox()

    def __createButtons(self):
            
        buttons = [
               {'name':'Quit','text':'QUIT','command':'Quit','side':tk.BOTTOM},
               {'name':'SpawnInputDialog','text':'Add Input Files','side':tk.LEFT},
               {'name':'RemoveFile','text':'Remove Files','side':tk.LEFT},
               {'name':'SpawnOutputDialog','text':'Choose Output Directory','side':tk.LEFT},
               {'name':'Parse','text':'Parse!','side':tk.LEFT}
               ]

        for b in buttons:
            button = ttk.Button(self.ButtonFrame)
            button.config(text=b['text'],command=getattr(self,b['name']+'Click'))
            button.pack(side=b['side'])
            setattr(self,'Button'+b['name'],button)
       
    def __createFileListBox(self):
        self.FileListBoxFrameLabelVar = tk.StringVar()
        self.FileListBoxFrameLabel = tk.Label(self.FileListBoxFrame,\
                textvariable=self.FileListBoxFrameLabelVar,\
                font=font.Font(size=10,weight="bold"))
        self.FileListBoxFrameLabel.pack(side=tk.TOP,fill=tk.X)

        self.InFileListBoxFrame = ttk.Frame(self.FileListBoxFrame)
        self.InFileListBoxFrame.pack(side=tk.LEFT, fill=tk.BOTH)
        
        yScroll = ttk.Scrollbar(self.InFileListBoxFrame,orient=tk.VERTICAL)
        yScroll.pack(side=tk.RIGHT,fill=tk.Y)
        xScroll = ttk.Scrollbar(self.InFileListBoxFrame, orient=tk.HORIZONTAL)
        xScroll.pack(side=tk.BOTTOM,fill=tk.X)
        self.filelist = tk.StringVar()
        self.FileListBox = tk.Listbox(self.InFileListBoxFrame, listvariable=self.filelist, 
                                      selectmode=tk.EXTENDED, 
                                      height = 20, width = 30, relief=tk.RAISED, bd=1,
                                      bg=cl.WHITE,
                                      #font=Font(size=10),
                                      xscrollcommand=xScroll.set, 
                                      yscrollcommand=yScroll.set)
        self.FileListBox.bind('<<ListboxSelect>>', self.ListBoxClick)
        xScroll['command'] = self.FileListBox.xview
        yScroll['command'] = self.FileListBox.yview
        self.FileListBox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.UpdateFileListBoxFrameLabel()
      
        self.PlotCanvas = tk.Canvas(self.FileListBoxFrame, height = 20, width=550)
        self.PlotCanvas.pack(side=tk.LEFT, fill=tk.BOTH)
        


        
    def ToFront(self):
        if platform.system() == "Darwin":
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        else:
            self.master.attributes('-topmost', 1)
            self.master.attributes('-topmost', 0)        

    def QuitClick(self):
        self.Quit()

    def ListBoxClick(self, event):
#        self.logger.info("Click click click")
#        self.handler.flush()
        print(event)
        selected = [self.FileListBox.get(x) for x in self.FileListBox.curselection()]
        if selected == self.selected_files:
            self.logger.debug("File selection unchanged.")
            self.handler.flush()
            return
        if len(selected) > 1:
            return
        self.selected_files = selected
        _f = os.path.join(self.indir, selected[-1])
        self.logger.debug("Got %s from list", _f)
        self.handler.flush()
        if os.path.exists(_f):
            self.DisplayDataFigure(_f)
        #filename = tk.PhotoImage(file = os.path.join(os.environ['HOME'],"Downloads","Dark Helmet.png"))
        #image = self.PlotCanvas.create_image(50, 50, anchor=tk.NE, image=filename)
#        coord = 10, 50, 240, 210
#        oval = self.PlotCanvas.create_arc(coord, start=0, extent=150, fill="red")

    def ParseClick(self):
        self.checkOptions()
        self.Parse()
            
    def SpawnInputDialogClick(self):
        self.checkOptions()
        self.indir = filedialog.askdirectory(title="Files to parse",  \
                        initialdir=self.cache['last_input_path'])
        self.cache['last_input_path'] = self.indir
        for _f in os.listdir(self.indir):
            if _f[-3:].lower() == self.opts.extension:
                if os.path.isfile(os.path.join(self.indir,_f)):
                    self.in_files.append(_f)
            else:
                self.logger.debug("Skipping %s", _f)
        if len(self.in_files):    
            self.updateFileListBox()

    def updateFileListBox(self):
        self.filelist.set(" ".join([x.replace(" ","_") for x in self.in_files]))
     
    def RemoveFileClick(self):
        self.checkOptions()
        selected = [self.FileListBox.get(x) for x in self.FileListBox.curselection()]
        todel = []
        filelist = []
        for i in range(0, len(self.in_files)):
            for s in selected:
                if self.in_files[i].replace(" ","_") == s:
                    todel.append(i)
        
        for i in range(0, len(self.in_files)):
            if i not in todel:
                       filelist.append(self.in_files[i])
        self.in_files = filelist
        self.updateFileListBox()
        self.FileListBox.selection_clear(0,tk.END)
                
    def SpawnOutputDialogClick(self):
        outdir = tk.filedialog.askdirectory(title="Select Output Directory", initialdir=self.outdir)
        if os.path.exists(outdir):
            self.outdir = outdir
            self.UpdateFileListBoxFrameLabel()

    def UpdateFileListBoxFrameLabel(self):
        self.FileListBoxFrameLabelVar.set("Output to: %s"% (self.outdir) )

    
    def Quit(self):
        self.master.destroy()

    def checkOptions(self):
        if self.cache['last_input_path'] == None:
            self.cache['last_input_path'] = os.environ['HOME']
        if not os.path.exists(self.cache['last_input_path']):
            self.cache['last_input_path'] = os.environ['HOME']
        print("Nothing Yet.")

    def Parse(self):
        print("Nothing here yet")
    
    
    def DisplayDataFigure(self, fileName):

        distanceData = []
        currentData = []
        with open(fileName, 'rb') as fileData:
            self.logger.debug("Plotting %s", fileName)
            self.handler.flush()
            for liness in fileData.readlines()[105:-1]:
                liness = liness.__str__()
                liness = liness[2:-9]
                liness = liness.split('\\t')
                distanceData.append(float(liness[0]))
                currentData.append(float(liness[1]))

        #https://matplotlib.org/gallery/user_interfaces/embedding_in_tk_canvas_sgskip.html
        fig = mpl.figure.Figure(figsize=(5, 4), dpi=80)
        ax = fig.add_subplot(111)
        ax.plot(distanceData, currentData)
           
        figure_canvas_agg = FigureCanvasAgg(fig)
        figure_canvas_agg.draw()
        figure_x, figure_y, figure_w, figure_h = fig.bbox.bounds
        figure_w, figure_h = int(figure_w), int(figure_h)
        fig_photo = tk.PhotoImage(master=self.PlotCanvas, width=figure_w, height=figure_h)
    
        # Position: convert from top-left anchor to center anchor
        self.PlotCanvas.create_image(figure_w/2, figure_h/2, image=fig_photo)
    
        # Unfortunately, there's no accessor for the pointer to the native renderer
        tkagg.blit(fig_photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)
    
        # Return a handle which contains a reference to the photo object
        # which must be kept live or else the picture disappears

        
        #try:
        #fig_photo.show()
        #except AttributeError:
        #    pass