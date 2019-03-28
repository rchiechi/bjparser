#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 13:18:21 2019

@author: rchiechi
"""
import os
import logging
import platform
import threading
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
from parse.read import ReadIVS


MASTER_LOCK = threading.RLock()


class BJParserFrame(tk.Frame):

    indir=str()
    outdir=str()
    Keep_selected_files = []
    Toss_selected_files = []
    Keep_files = []
    Toss_files = []
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
        self.cache = Cache(self.logger)
        self.ivs_files = ReadIVS(self.logger, self.opts)
        self.checkOptions()
        self.ToFront()
        self.mainloop()

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
               {'name':'TossFile','text':'Toss Files','side':tk.LEFT},
               {'name':'KeepFile','text':'Keep Files','side':tk.LEFT},
               {'name':'SpawnOutputDialog','text':'Choose Output Directory','side':tk.LEFT},
               {'name':'Parse','text':'Parse!','side':tk.LEFT}
               ]

        for b in buttons:
            button = ttk.Button(self.ButtonFrame)
            button.config(text=b['text'],command=getattr(self,b['name']+'Click'))
            button.pack(side=b['side'])
            setattr(self,'Button'+b['name'],button)
        
        self.master.bind('<Left>', self.KeepFileClick)
        self.master.bind('<Right>', self.TossFileClick)
       
    def __createFileListBox(self):
        _h = int(self.winfo_height())
        _w = int(self.winfo_width())
        
        self.FileListBoxFrameLabelVar = tk.StringVar()
        self.FileListBoxFrameLabel = tk.Label(self,
                textvariable=self.FileListBoxFrameLabelVar,
                font=font.Font(size=10,weight="bold"))
        self.FileListBoxFrameLabel.pack(side=tk.TOP,fill=tk.X)
        
        scrolls = {}
        styles = {'Keep': (tk.LEFT, cl.LIGHTGREEN),
                  'Toss': (tk.RIGHT, cl.LIGHTRED)}
        for _prefix in ('Keep', 'Toss'):
            setattr(self, _prefix+'FileListBoxFrame', ttk.Frame(self.FileListBoxFrame, height = _h/3, width = _w/2))   
            getattr(self, _prefix+'FileListBoxFrame').pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrolls[_prefix+'yScroll']=ttk.Scrollbar(getattr(self, _prefix+'FileListBoxFrame'), orient=tk.VERTICAL)
            scrolls[_prefix+'yScroll'].pack(side=styles[_prefix][0], fill=tk.Y)
            scrolls[_prefix+'xScroll']=ttk.Scrollbar(getattr(self, _prefix+'FileListBoxFrame'), orient=tk.HORIZONTAL)
            scrolls[_prefix+'xScroll'].pack(side=tk.BOTTOM, fill=tk.X)
            setattr(self, _prefix+'filelist', tk.StringVar())
                      
            setattr(self, _prefix+'FileListBox', tk.Listbox(getattr(self, _prefix+'FileListBoxFrame'),
                                                            listvariable=getattr(self, _prefix+'filelist'), 
                                      selectmode=tk.EXTENDED, 
                                      height = 20, width = 45, relief=tk.RAISED, bd=1,
                                      bg=styles[_prefix][1], 
                                      #font=Font(size=10),
                                      xscrollcommand=scrolls[_prefix+'xScroll'].set, 
                                      yscrollcommand=scrolls[_prefix+'yScroll'].set))
            
            getattr(self, _prefix+'FileListBox').bind('<<ListboxSelect>>', getattr(self, _prefix+'ListBoxClick'))
            scrolls[_prefix+'xScroll']['command'] = getattr(self, _prefix+'FileListBox').xview
            scrolls[_prefix+'yScroll']['command'] = getattr(self, _prefix+'FileListBox').yview
            getattr(self, _prefix+'FileListBox').pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
      
    def __createCanvas(self):
        _h = int(self.winfo_height())
        _w = int(self.winfo_width())
        self.KeepPlotCanvas = tk.Canvas(self.CanvasFrame, bg='white',
                                        height = _h/3, width = _w/2)
        self.KeepPlotCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.TossPlotCanvas = tk.Canvas(self.CanvasFrame, bg='white',
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
        self.__ListBoxClick('Keep')


    def TossListBoxClick(self, event):
        self.__ListBoxClick('Toss')


    def __ListBoxClick(self, _prefix):
        selected = [getattr(self, _prefix+'FileListBox').get(x) 
                for x in getattr(self, _prefix+'FileListBox').curselection()]
        if selected == getattr(self, _prefix+'_selected_files'):
            self.logger.debug("%s file selection unchanged.", _prefix)
            self.handler.flush()
            return
        if len(selected) > 1:
            return
        setattr(self, _prefix+'_selected_files', selected)
        _f = os.path.join(self.indir, selected[-1])
        self.logger.debug("Got %s from %s list", _f, _prefix)
        self.handler.flush()
        if os.path.exists(_f):
            self.DisplayDataFigure(_prefix, 
                                   getattr(self, _prefix+'PlotCanvas'), _f)
        
            

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
                    self.Keep_files.append(_f)
            else:
                self.logger.debug("Skipping %s", _f)
        if len(self.Keep_files):    
            self.updateKeepFileListBox()
            

    def updateKeepFileListBox(self):
        self.__updateFileListBox('Keep')

    def updateTossFileListBox(self):
        self.__updateFileListBox('Toss')

    def __updateFileListBox(self, _prefix):
            getattr(self, _prefix+'filelist').set(" ".join([x.replace(" ","_") 
                for x in getattr(self, _prefix+'_files')]))
#            for _f in getattr(self, _prefix+'_files'):
#                getattr(self.ivs_files, _prefix+'File')(os.path.join(self.indir,_f))


    def KeepFileClick(self, event=None):
        self.__FileClick('Toss', 'Keep')
        
    def TossFileClick(self, event=None):
        self.__FileClick('Keep', 'Toss')
  
    def __FileClick(self, _from, _to):      
        self.checkOptions()
        selected = [getattr(self, _from+'FileListBox').get(x) 
                    for x in getattr(self, _from+'FileListBox').curselection()]
        tomove = []
        filelist = []
        for i in range(0, len(getattr(self, _from+'_files'))):
            for s in selected:
                if getattr(self, _from+'_files')[i].replace(" ","_") == s:
                    tomove.append(i)
        
        for i in range(0, len(getattr(self, _from+'_files'))):
            if i not in tomove:
                filelist.append(getattr(self, _from+'_files')[i])
            else:
                getattr(self, _to+'_files').append(getattr(self, _from+'_files')[i])
        setattr(self, _from+'_files', filelist)
        getattr(self, _from+'FileListBox').selection_clear(0,tk.END)
        #getattr(self, _from+'FileListBox').selection_set(selected[-1])
        self.__updateFileListBox(_to)
        self.__updateFileListBox(_from)
        
    def SpawnOutputDialogClick(self):
        outdir = tk.filedialog.askdirectory(title="Select Output Directory", initialdir=self.outdir)
        if os.path.exists(outdir):
            self.outdir = outdir
            self.UpdateFileListBoxFrameLabel()

    
    def Quit(self):
        self.master.destroy()

    def checkOptions(self):       
        if not self.cache['last_input_path']:
            self.cache['last_input_path'] = os.getcwd()
        if not os.path.exists(self.cache['last_input_path']):
            self.last_input_path = os.path.expanduser('~')
        if not self.outdir:
            self.outdir = os.path.join(self.indir, 'parsed')
        self.FileListBoxFrameLabelVar.set("Output to: %s"% (self.outdir) )
        

    def Parse(self):
        print("Nothing here yet")
    
    def DisplayDataFigure(self, label, master, fileName):
        self.ivs_files.AddFile(fileName)
        self.handler.flush()
        fig = mpl.figure.Figure(figsize=(5, 4), dpi=80)
        ax = fig.add_subplot(111)
        ax.plot(self.ivs_files[fileName]['d'], self.ivs_files[fileName]['I'])
        fig.suptitle(os.path.basename(fileName))
        figure_canvas_agg = FigureCanvasAgg(fig)
        figure_canvas_agg.draw()
        figure_x, figure_y, figure_w, figure_h = fig.bbox.bounds
        figure_w, figure_h = int(figure_w), int(figure_h)
        #https://matplotlib.org/gallery/user_interfaces/embedding_in_tk_canvas_sgskip.html
        setattr(self, label+'fig_photo', tk.PhotoImage(master=master, width=figure_w, height=figure_h))
        getattr(self, label+'PlotCanvas').create_image(figure_w/2, 
               figure_h/2, image=getattr(self, label+'fig_photo'))    
        # Unfortunately, there's no accessor for the pointer to the native renderer
        tkagg.blit(getattr(self, label+'fig_photo'), figure_canvas_agg.get_renderer()._renderer, colormode=2)
