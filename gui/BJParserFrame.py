#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 13:18:21 2019

@author: rchiechi
"""
import os
#import sys
import logging
import platform
import threading
import numpy as np
import queue
import time
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
#import matplotlib as mpl
#mpl.use('TkAgg')
#import matplotlib.pyplot as plt
#import matplotlib.backends.tkagg as tkagg
#from matplotlib.backends.backend_agg import FigureCanvasAgg
import gui.colors as cl
#import gui.tooltip as tip
from util.Cache import Cache
from util.logger import GUIHandler
from parse.read import ReadIVS
from plot.canvasplotter import XYplot, XYZplot, Histplot
from parse.GHistogram import GHistogram
from parse.write import Ghistwriter
#from parse.Guess import CountPlateaux
from parse.Guess import CountThread
#from gui.BusyWidget import BusyWidget
#import matplotlib.pyplot as plt
#import matplotlib.backends.tkagg as tkagg



MASTER_LOCK = threading.RLock()

class BJParserFrame(tk.Frame):

    indir=str()
    outdir=str()
#    Keep_selected_files = []
#    Toss_selected_files = []
    style = ttk.Style()
    child_threads = []
    all_files_parsed = False


    boolmap = {1:True, 0:False}
    
    def __init__(self, opts, master=None):
        tk.Frame.__init__(self, master)
        self.opts = opts
        self.alive = threading.Event()
        self.alive.set()
        self.master.tk_setPalette(background=cl.GREY,
                                  activeBackground=cl.GREY)
        self.master.title("RCCLab STMBJ Data Parser")
        self.master.geometry('900x850+250-250')
        self.pack(fill=tk.BOTH, expand=True)
        self.update_idletasks()
        self.__createWidgets()
        self.cache = Cache(self.logger)
        self.ivs_files = ReadIVS(self.logger, MASTER_LOCK, self.opts)
        self.checkOptions()
        self.ToFront()     
        self.after('1000', self.WaitForThreads)
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
                {'name':'Reset','text':'Reset','command':'Reset','side':tk.BOTTOM},
                {'name':'SpawnInputDialog','text':'Input Directory','side':tk.LEFT},
                {'name':'TossFile','text':'Toss','side':tk.LEFT},
                {'name':'KeepFile','text':'Keep','side':tk.LEFT},
                {'name':'ArchiveTossed','text':'Archive Tossed','side':tk.LEFT},
                {'name':'SpawnOutputDialog','text':'Output Directory','side':tk.LEFT},
                {'name':'Guess','text':'Guess Which Plots to Toss', 'side':tk.LEFT},
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
        self.alive.clear()
        print("Quitting...")
        self.Quit()

    def KeepListBoxClick(self, event):
        self.__ListBoxClick('Keep')

    def TossListBoxClick(self, event):
        self.__ListBoxClick('Toss')

    def __ListBoxClick(self, _prefix):
        selected = [getattr(self, _prefix+'FileListBox').get(x).replace("_"," ") 
                for x in getattr(self, _prefix+'FileListBox').curselection()]
#        if selected == getattr(self, _prefix+'_selected_files'):
#            self.logger.debug("%s file selection unchanged.", _prefix)
#            self.handler.flush()
#            return

#        setattr(self, _prefix+'_selected_files', selected)
        if len(selected) == 1:
            self.DisplayDataFigure(_prefix, 
                                   getattr(self, _prefix+'PlotCanvas'), selected[-1])
        elif len(selected) > 1:
            self.DisplayDataFigures(_prefix, 
                                   getattr(self, _prefix+'PlotCanvas'), selected)
    
    def GuessClick(self):
        if not hasattr(self, 'selection_cache'):
            self.logger.error("No files loaded")
            self.handler.flush()
            return
        if not self.all_files_parsed:
            self.logger.error("Wait for parser to complete")
            return
        self.child_threads.append({'thread':threading.Thread(target=self.doGuess),
                                    'widgets':[self.ButtonGuess,
                                               self.ButtonParse,
                                               self.KeepFileListBox, 
                                               self.TossFileListBox]})
        self.child_threads[-1]['thread'].name = 'Plateaux Guesser'
        self.child_threads[-1]['thread'].start()
        
    def doGuess(self):
        self.logger.info("Starting search for plateaux...")
        guessQ = queue.Queue()
        for fn in self.selection_cache['Keep_files']:
            _fn = os.path.join(self.indir, fn)
            guessQ.put((fn, self.ivs_files[_fn]['d'], self.ivs_files[_fn]['I']))
            
        children = []
        for i in range(0,8):
            children.append(CountThread(self.alive, guessQ))
            children[-1].start()
        
        while not guessQ.empty():
            kept = 0
            last_kept = kept
            for c in children:
                kept += len(c.keep)
            if kept != last_kept:
                self.logger.info("Keeping %s traces", kept)
        _keep = []
        _toss = []
        for c in children:
            _keep += c.keep
            _toss += c.toss
        _keep.sort()
        _toss.sort()
        self.logger.info("Search for plateaux done.")
        self.selection_cache['Keep_files'] = _keep
        self.selection_cache['Toss_files'] = _toss             
        self.__updateFileListBox('Toss')
        self.__updateFileListBox('Keep')
        self.__ListBoxClick('Keep')
        
        kept = len(self.selection_cache['Keep_files']) 
        tossed = len(self.selection_cache['Toss_files'])
        self.logger.info("Kept %0.1f%% of traces.", (kept/(kept+tossed))*100)
        
    def ParseClick(self):
        if not hasattr(self, 'selection_cache'):
            self.logger.error("No files selected.")
            self.handler.flush()
            return
        self.checkOptions()
        self.child_threads.append({'thread':threading.Thread(target=self.Parse),
                                   'widgets':[self.ButtonParse, 
                                              self.KeepFileListBox, 
                                              self.TossFileListBox]})
        self.child_threads[-1]['thread'].name = 'G-histogram parser'
        self.child_threads[-1]['thread'].start()
        #self.Parse()
    
    def ResetClick(self):
        self.logger.info("Killing background tasks")
        self.alive.clear()
        self.handler.flush()
        time.sleep(3)
        self.alive.set()      
        self.SpawnInputDialogClick(True)
    
    def SpawnInputDialogClick(self, reset=False):

        self.checkOptions()
        self.indir = filedialog.askdirectory(title="Files to parse",  \
                        initialdir=self.cache['last_input_path'])
        if os.path.exists(self.indir):
            self.cache['last_input_path'] = self.indir
        else:
            return
        if reset:
            try:
                os.unlink(os.path.join(
                self.indir, 'STMBJParse.cache'))
            except IOError:
                pass
        self.selection_cache = Cache(self.logger, os.path.join(
                self.indir, 'STMBJParse.cache'))
        if not self.selection_cache['Keep_files']:
            self.selection_cache['Keep_files'] = []      
        if not self.selection_cache['Toss_files']:
            self.selection_cache['Toss_files'] = []
        fns = os.listdir(self.indir)
        fns.sort()
        if not self.selection_cache['Keep_files']:
            for _f in fns:
                if _f[-3:].lower() == self.opts.extension:
                    if os.path.isfile(os.path.join(self.indir,_f)):
                        self.selection_cache['Keep_files'].append(_f)
                else:
                    self.logger.debug("Skipping %s", _f)
        if len(self.selection_cache['Keep_files']):    
            self.updateKeepFileListBox()
            self.updateTossFileListBox()
        self.logger.debug("Input directory is %s", self.indir)
        if not self.outdir:
            self.outdir = os.path.join(self.indir, 'parsed')
        self.checkOptions()
        self.child_threads.append({'thread':threading.Thread(target=self.BackgroundParseFiles),
                                    'widgets':[self.ButtonGuess,
                                               self.ButtonReset,
                                               self.ButtonArchiveTossed]})
        self.child_threads[-1]['thread'].name = 'IVS File parser'
        self.child_threads[-1]['thread'].start()
        
    def BackgroundParseFiles(self): 
        self.logger.info("Background IVS file parsing started.")
        for _fn in self.selection_cache['Keep_files']:
            if not self.alive.is_set():
                return
            fn = os.path.join(self.indir, _fn)
            self.ivs_files.AddFile(fn)
        self.all_files_parsed = True
        self.logger.info("Background IVS file parsing complete.")         
        
    def WaitForThreads(self):
        if len(self.child_threads):
#            print("THREAD RUNNING")
            c = self.child_threads.pop()
            if c['thread'].is_alive():
                if 'widgets' in c:
                    for w in c['widgets']:
                        w['state'] = tk.DISABLED
                self.child_threads.append(c)
            else:
                if 'widgets' in c:
                    for w in c['widgets']:
                        w['state'] = tk.NORMAL
                if 'after' in c:
                    tk.messagebox.showinfo("Complete", "%s completed." % c['thread'].name)
                    c['after'][0](*c['after'][1])               
        self.after('1000', self.WaitForThreads)
        
    def ArchiveTossedClick(self):
        if not hasattr(self, 'selection_cache'):
            return
        if not len(self.selection_cache['Toss_files']):
            self.logger.info("No files to toss.")
            return
        archive_dir = os.path.join(self.indir, 'TossedArchive')
        if not os.path.exists(archive_dir):
            os.mkdir(archive_dir)
        while len(self.selection_cache['Toss_files']):
            fn = self.selection_cache['Toss_files'].pop()
            os.rename(os.path.join(self.indir, fn),
                      os.path.join(archive_dir, fn))
            self.logger.info("Archived %s", fn)
            self.handler.flush()
        self.__updateFileListBox('Toss')
            
           
    def updateKeepFileListBox(self):
        self.__updateFileListBox('Keep')

    def updateTossFileListBox(self):
        self.__updateFileListBox('Toss')

    def __updateFileListBox(self, _prefix):
            getattr(self, _prefix+'filelist').set(" ".join([x.replace(" ","_") 
                for x in self.selection_cache[_prefix+'_files']]))
#            getattr(self, _prefix+'filelist').set(" ".join([x.replace(" ","_") 
#                for x in self.selection_cache[_prefix+'_files']]))
            if len(self.selection_cache[_prefix+'_files']) == 0:
                setattr(self, _prefix+'fig_photo', None)

    def KeepFileClick(self, event=None):
        self.__FileClick('Toss', 'Keep')
        
    def TossFileClick(self, event=None):
        self.__FileClick('Keep', 'Toss')
  
    def __FileClick(self, _from, _to):      
        self.checkOptions()
        selected = [getattr(self, _from+'FileListBox').get(x).replace("_"," ") 
                    for x in getattr(self, _from+'FileListBox').curselection()]
        if selected:
            idx = getattr(self, _from+'FileListBox').curselection()[0]
        else:
            idx = -1
        tomove = []
        filelist = []
        for i in range(0, len(self.selection_cache[_from+'_files'])):
            for s in selected:
                if self.selection_cache[_from+'_files'][i] == s:
                    tomove.append(i)
        
        for i in range(0, len(self.selection_cache[_from+'_files'])):
            if i not in tomove:
                filelist.append(self.selection_cache[_from+'_files'][i])
            else:
                self.selection_cache[_to+'_files'].append(self.selection_cache[_from+'_files'][i])
        self.selection_cache[_from+'_files'] = filelist
        getattr(self, _from+'FileListBox').selection_clear(0,tk.END)
        if idx > -1:
            getattr(self, _from+'FileListBox').activate(idx)
            getattr(self, _from+'FileListBox').selection_set(idx)
        self.__updateFileListBox(_to)
        self.__updateFileListBox(_from)
        self.__ListBoxClick(_from)
        
        
    def SpawnOutputDialogClick(self):
        if not self.outdir and self.indir:
            self.outdir = self.indir
        outdir = tk.filedialog.askdirectory(title="Select Output Directory", 
                                            initialdir=self.outdir)
        if os.path.exists(outdir):
            self.outdir = outdir
        self.checkOptions()
    
    def Quit(self):
        for c in self.child_threads:
            try:
                c['thread'].join(timeout=10)
            except RuntimeError:
                print("Thread %s not started yet" % c['thread'].name)
        self.master.destroy()

    def checkOptions(self):       
        if not self.cache['last_input_path']:
            self.cache['last_input_path'] = os.getcwd()
        if not os.path.exists(self.cache['last_input_path']):
            self.last_input_path = os.path.expanduser('~')
#        if not self.outdir:
#            self.outdir = os.path.join(self.indir, 'parsed')
#            self.logger.debug("Set outdir to %s", self.outdir)
        self.handler.flush()
        self.FileListBoxFrameLabelVar.set("Output to: %s"% (self.outdir) )



    def Parse(self):
        self.logger.info("Reading file selection...")
        self.handler.flush()
        X = np.array([])
        for _fn in self.selection_cache['Keep_files']:
            if not self.alive.is_set():
                break
            fn = os.path.join(self.indir, _fn)
            self.ivs_files.AddFile(fn)    
            X = np.append(X, self.ivs_files[fn]['I'])
        self.logger.info("Done!")
        self.handler.flush()
        Ghist = GHistogram(self.logger, X)
        self.DisplayHistogramData('Keep', self.KeepPlotCanvas, Ghist)
        Ghistwriter(self.logger, self.outdir, Ghist)


    def DisplayHistogramData(self, label, master, hist):
        
        labels={'title':'G Histogram',
                'X': 'G/G0',
                'Y': 'Frequency'}
        plotter = Histplot(hist.fits['bins'], 
                           hist.fits['freq'],
                           hist.fits['fit'],
                           labels)

        plotter.Draw(tk.PhotoImage(master=master,
                                   width=plotter.figure_w,
                                   height=plotter.figure_h))
        getattr(self, label+'PlotCanvas').create_image(plotter.figure_w/2, 
               plotter.figure_h/2, image=plotter.fig_photo)
        setattr(self, label+'fig_photo', plotter)

    
    def DisplayDataFigure(self, label, master, _fn):
        #https://matplotlib.org/gallery/user_interfaces/embedding_in_tk_canvas_sgskip.html
        fn = os.path.join(self.indir, _fn)
        self.ivs_files.AddFile(fn)
        self.handler.flush()      
        labels={'title':os.path.basename(fn),
                'X': 'distance',
                'Y': 'current'}
        plotter = XYplot(self.ivs_files[fn]['d'],                       
                         self.ivs_files[fn]['I'],
                         labels)
        plotter.Draw(tk.PhotoImage(master=master,
                                   width=plotter.figure_w,
                                   height=plotter.figure_h))
        #plotter.Draw(fig_photo)
        getattr(self, label+'PlotCanvas').create_image(plotter.figure_w/2, 
               plotter.figure_h/2, image=plotter.fig_photo)
        setattr(self, label+'fig_photo', plotter)

    def DisplayDataFigures(self, label, master, fns):
        #https://matplotlib.org/gallery/user_interfaces/embedding_in_tk_canvas_sgskip.html
        _title = ''
       
        X, Y, Z = [], [], []
        for _fn in fns:
            fn = os.path.join(self.indir, _fn)
            self.ivs_files.AddFile(fn)
            self.handler.flush()
            _title += os.path.basename(fn)+' '
            X.append([])
            Y.append([])
            Z.append([])
            for i in range(0, len(self.ivs_files[fn]['I'])):
                X[-1].append(self.ivs_files[fn]['d'][i])
                Y[-1].append(self.ivs_files[fn]['I'][i])

        
        labels={'title':_title,
                'X': 'distance',
                'Y': 'trace',
                'Z': 'current'}
        plotter = XYZplot(X, Y, labels)
        
        plotter.Draw(tk.PhotoImage(master=master,
                                   width=plotter.figure_w,
                                   height=plotter.figure_h))
        #plotter.Draw(fig_photo)
        getattr(self, label+'PlotCanvas').create_image(plotter.figure_w/2, 
               plotter.figure_h/2, image=plotter.fig_photo)
        setattr(self, label+'fig_photo', plotter)
