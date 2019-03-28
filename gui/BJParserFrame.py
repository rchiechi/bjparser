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
mpl.use('TkAgg')
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
    keep_selected_files = []
    toss_selected_files = []
    in_files = []
    style = ttk.Style()
    boolmap = {1:True, 0:False}
    
    def __init__(self, opts, master=None):
        tk.Frame.__init__(self, master)
        self.opts = opts        
        self.master.tk_setPalette(background=cl.GREY,
                                  activeBackground=cl.GREY)
        self.master.title("RCCLab STMBJ Data Parser")
        self.master.geometry('900x850+250-250')
        self.pack(fill=tk.BOTH, expand=True)
        self.update_idletasks() 
        self.__createWidgets()
        self.__loadcache()
        self.ToFront()
        self.mainloop()
        
    def __loadcache(self):
        self.cache = Cache(self.logger)
        if not self.cache['last_input_path']:
            self.cache['last_input_path'] = os.getcwd()
        if not os.path.exists(self.cache['last_input_path']):
            self.last_input_path = os.path.expanduser('~') 
        
    def __createWidgets(self):
        self.update()
        
        self.ButtonFrame = ttk.Frame(self)
        self.LoggingFrame = ttk.Frame(self)
        self.FileListBoxFrame = ttk.Frame(self)
        self.CanvasFrame = ttk.Frame(self)

        yScroll = ttk.Scrollbar(self.LoggingFrame, orient=tk.VERTICAL)
        self.Logging = tk.Text(self.LoggingFrame, height=10, width=0,  
                bg=cl.BLACK, fg=cl.WHITE, yscrollcommand=yScroll.set)
        yScroll['command'] = self.Logging.yview
        self.Logging.pack(side=tk.BOTTOM,fill=tk.BOTH,expand=True)
        yScroll.pack(side=tk.RIGHT,fill=tk.Y)

        self.__createButtons()
        self.__createFileListBox()
        self.__createCanvas()

        self.CanvasFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.FileListBoxFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.ButtonFrame.pack(side=tk.BOTTOM,fill=None)
        self.LoggingFrame.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.logger = logging.getLogger('parser.gui')
        self.handler = GUIHandler(self.Logging)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(getattr(logging,self.opts.loglevel.upper()))
        self.logger.info("Logging...")
        self.handler.flush()
        

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
        _h = int(self.winfo_height())
        _w = int(self.winfo_width())
        
        self.FileListBoxFrameLabelVar = tk.StringVar()
        self.FileListBoxFrameLabel = tk.Label(self,
                textvariable=self.FileListBoxFrameLabelVar,
                font=font.Font(size=10,weight="bold"))
        self.FileListBoxFrameLabel.pack(side=tk.TOP,fill=tk.X)
        
        
#        self.style.configure('Keep.TFrame', background='blue')
        self.KeepFileListBoxFrame = ttk.Frame(self.FileListBoxFrame, height = _h/3, width = _w/2)
        self.KeepFileListBoxFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        KeepyScroll = ttk.Scrollbar(self.KeepFileListBoxFrame,orient=tk.VERTICAL)
        KeepyScroll.pack(side=tk.LEFT,fill=tk.Y)
        KeepxScroll = ttk.Scrollbar(self.KeepFileListBoxFrame, orient=tk.HORIZONTAL)
        KeepxScroll.pack(side=tk.BOTTOM,fill=tk.X)
        self.keepfilelist = tk.StringVar()
        self.KeepFileListBox = tk.Listbox(self.KeepFileListBoxFrame, listvariable=self.keepfilelist, 
                                      selectmode=tk.EXTENDED, 
                                      height = 20, width = 45, relief=tk.RAISED, bd=1,
                                      bg=cl.LIGHTGREEN,
                                      #font=Font(size=10),
                                      xscrollcommand=KeepxScroll.set, 
                                      yscrollcommand=KeepyScroll.set)
        self.KeepFileListBox.bind('<<ListboxSelect>>', self.KeepListBoxClick)
        KeepxScroll['command'] = self.KeepFileListBox.xview
        KeepyScroll['command'] = self.KeepFileListBox.yview
        self.KeepFileListBox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        
#        self.style.configure('Toss.TFrame', background='yellow')        
        self.TossFileListBoxFrame = ttk.Frame(self.FileListBoxFrame, height = _h/3, width = _w/2)
        self.TossFileListBoxFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        TossyScroll = ttk.Scrollbar(self.TossFileListBoxFrame,orient=tk.VERTICAL)
        TossyScroll.pack(side=tk.RIGHT,fill=tk.Y)
        TossxScroll = ttk.Scrollbar(self.TossFileListBoxFrame, orient=tk.HORIZONTAL)
        TossxScroll.pack(side=tk.BOTTOM,fill=tk.X)
        self.tossfilelist = tk.StringVar()
        self.TossFileListBox = tk.Listbox(self.TossFileListBoxFrame, listvariable=self.tossfilelist, 
                                      selectmode=tk.EXTENDED, 
                                      height = 20, width = 45, relief=tk.RAISED, bd=1,
                                      bg=cl.LIGHTRED,
                                      #font=Font(size=10),
                                      xscrollcommand=TossxScroll.set, 
                                      yscrollcommand=TossyScroll.set)
        self.TossFileListBox.bind('<<ListboxSelect>>', self.TossListBoxClick)
        TossxScroll['command'] = self.TossFileListBox.xview
        TossyScroll['command'] = self.TossFileListBox.yview
        self.TossFileListBox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.UpdateFileListBoxFrameLabel()
      
    def __createCanvas(self):
        _h = int(self.winfo_height())
        _w = int(self.winfo_width())
        print(self.winfo_geometry())
        print(_h)
        print(_w)
        self.KeepPlotCanvas = tk.Canvas(self.CanvasFrame, bg='green',
                                        height = _h/3, width = _w/2)
        self.KeepPlotCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.TossPlotCanvas = tk.Canvas(self.CanvasFrame, bg='red',
                                        height = _h/3, width = _w/2)
        self.TossPlotCanvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)


        
    def ToFront(self):
        if platform.system() == "Darwin":
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        else:
            self.master.attributes('-topmost', 1)
            self.master.attributes('-topmost', 0)        

    def QuitClick(self):
        self.Quit()

    def KeepListBoxClick(self, event):

        selected = [self.KeepFileListBox.get(x) for x in self.KeepFileListBox.curselection()]
        if selected == self.keep_selected_files:
            self.logger.debug("Keep file selection unchanged.")
            self.handler.flush()
            return
        if len(selected) > 1:
            return
        self.keep_selected_files = selected
        _f = os.path.join(self.indir, selected[-1])
        self.logger.debug("Got %s from keep list", _f)
        self.handler.flush()
        if os.path.exists(_f):
            self.DisplayDataFigure('Keep', self.KeepPlotCanvas, _f)

    def TossListBoxClick(self, event):

        selected = [self.TossFileListBox.get(x) for x in self.TossFileListBox.curselection()]
        if selected == self.toss_selected_files:
            self.logger.debug("Toss file selection unchanged.")
            self.handler.flush()
            return
        if len(selected) > 1:
            return
        self.toss_selected_files = selected
        _f = os.path.join(self.indir, selected[-1])
        self.logger.debug("Got %s from toss list", _f)
        self.handler.flush()
        if os.path.exists(_f):
            self.DisplayDataFigure('Toss', self.TossPlotCanvas, _f)
            
#    def ListBoxClick(self, event):
#
#        selected = [self.TossFileListBox.get(x) for x in self.TossFileListBox.curselection()]
#        if selected == self.toss_selected_files:
#            self.logger.debug("File selection unchanged.")
#            self.handler.flush()
#            return
#        if len(selected) > 1:
#            return
#        self.toss_selected_files = selected
#        _f = os.path.join(self.indir, selected[-1])
#        self.logger.debug("Got %s from toss list", _f)
#        self.handler.flush()
#        if os.path.exists(_f):
#            self.DisplayDataFigure('toss', self.TossPlotCanvas, _f)

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
            self.updateKeepFileListBox()
            

    def updateKeepFileListBox(self):
        self.keepfilelist.set(" ".join([x.replace(" ","_") for x in self.in_files]))
#    def updateTossFileListBox(self):
#        self.tossfilelist.set(" ".join([x.replace(" ","_") for x in self.in_files]))
     
    def RemoveFileClick(self):
        self.checkOptions()
        selected = [self.KeepFileListBox.get(x) for x in self.KeepFileListBox.curselection()]
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
        self.KeepFileListBox.selection_clear(0,tk.END)
                
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
    
    
    def DisplayDataFigure(self, label, master, fileName):

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
        fig.suptitle(os.path.basename(fileName))
        figure_canvas_agg = FigureCanvasAgg(fig)
        figure_canvas_agg.draw()
        figure_x, figure_y, figure_w, figure_h = fig.bbox.bounds
        figure_w, figure_h = int(figure_w), int(figure_h)
        #self.fig_photo = tk.PhotoImage(master=master, width=figure_w, height=figure_h)
        setattr(self, label+'fig_photo', tk.PhotoImage(master=master, width=figure_w, height=figure_h))
    
        # Position: convert from top-left anchor to center anchor
        getattr(self, label+'PlotCanvas').create_image(figure_w/2, 
               figure_h/2, image=getattr(self, label+'fig_photo'))
        #self.PlotCanvas.create_image(figure_w/2, figure_h/2, image=self.fig_photo)
    
        # Unfortunately, there's no accessor for the pointer to the native renderer
        tkagg.blit(getattr(self, label+'fig_photo'), figure_canvas_agg.get_renderer()._renderer, colormode=2)
