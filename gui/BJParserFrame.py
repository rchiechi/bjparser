#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 13:18:21 2019

@author: rchiechi
"""
import os
import logging
import threading
import queue
import time
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
import numpy as np
from plot.canvasplotter import getXYplot, getXYZplot, getHistplot
import gui.tkutil as util
import gui.colors as cl
from util.Cache import Cache
from util.logger import GUIHandler
from parse.read import ReadIVS
from parse.GHistogram import GHistogram
from parse.write import Ghistwriter
from parse.Guess import CountThread


__ALL__ = ['BJParserFrame']

MASTER_LOCK = threading.RLock()

#pylint: disable = attribute-defined-outside-init

class BJParserFrame(ttk.Frame):
    '''
    A TK Frame to hold the file list and plotting canvases for
    selecting and visualizing data from an STMBJ experiment
    '''
    indir=str()
    outdir=str()
    child_threads = []
    all_files_parsed = False
    boolmap = {1:True, 0:False}
    sidemap = {'Keep': tk.LEFT, 'Toss': tk.RIGHT}

    def __init__(self, opts):
        ttk.Frame.__init__(self, parent=None)
        self.opts = opts
        self.keeptoss = 'Keep'
        self.alive = threading.Event()
        self.alive.set()
        self.master.tk_setPalette(background=cl.GREY,
                                  activeBackground=cl.GREY)
        self.master.title("RCCLab STMBJ Data Parser")
        # self.master.geometry('900x850+250-250')
        self.pack(fill=tk.BOTH, expand=True)
        self.update_idletasks()
        self.__createWidgets()
        self.cache = Cache(self.logger)
        self.ivs_files = ReadIVS(self.logger, MASTER_LOCK, self.opts)
        self.checkOptions()
        util.bring_to_front(self)
        self.after('1000', self.WaitForThreads)
        #self.mainloop()


    def __createWidgets(self):
        self.update()
        # _h = int(self.winfo_height())
        # _w = int(self.winfo_width())

        self.ButtonFrame = ttk.Frame(self)
        self.LoggingFrame = ttk.Frame(self)
        self.MainFrame = ttk.PanedWindow(self, orient=tk.VERTICAL, width=1000)
        self.FileListBoxFrame = ttk.Frame(self.MainFrame, width=1000)
        self.CanvasFrame = ttk.PanedWindow(self.MainFrame, orient=tk.HORIZONTAL, width=1000)
        self.KeepCanvasFrame = ttk.Frame(self.CanvasFrame,
                height = 500, width = 800, style='Keep.TFrame' )
        self.TossCanvasFrame = ttk.Frame(self.CanvasFrame,
                height = 500, width = 200,  style='Toss.TFrame' )

        yScroll = ttk.Scrollbar(self.LoggingFrame, orient=tk.VERTICAL)
        self.Logging = tk.Text(self.LoggingFrame, height=10, width=0,
                bg=cl.BLACK, fg=cl.WHITE, yscrollcommand=yScroll.set)
        yScroll['command'] = self.Logging.yview
        self.Logging.pack(side=tk.BOTTOM,fill=tk.BOTH,expand=True)
        yScroll.pack(side=tk.RIGHT,fill=tk.Y)

        self.__createButtons()
        self.__createFileListBox()
        self.KeepPlotCanvas = None
        self.TossPlotCanvas = None
        self.KeepToolBar = None
        self.TossToolBar = None

        self.CanvasFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.MainFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.CanvasFrame.add(self.KeepCanvasFrame)
        self.CanvasFrame.add(self.TossCanvasFrame)
        self.MainFrame.add(self.CanvasFrame)
        self.MainFrame.add(self.FileListBoxFrame)
        self.ButtonFrame.pack(side=tk.BOTTOM, fill=tk.Y, expand=False)
        self.LoggingFrame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False)
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
            button = ttk.Button(self.ButtonFrame, takefocus=0)
            button.config(text=b['text'],command=getattr(self,b['name']+'Click'))
            button.pack(side=b['side'])
            setattr(self,'Button'+b['name'],button)


    def __createFileListBox(self):
        self.FileListBoxFrameLabelVar = tk.StringVar()
        self.FileListBoxFrameLabel = tk.Label(self,
                textvariable=self.FileListBoxFrameLabelVar,
                font=font.Font(size=10,weight="bold"))
        self.FileListBoxFrameLabel.pack(side=tk.TOP,fill=tk.X)

        scrolls = {}
        styles = {'Keep': (tk.LEFT, cl.LIGHTGREEN,'hand2'),
                  'Toss': (tk.RIGHT, cl.LIGHTRED, 'hand1')}
        for _prefix in ('Keep', 'Toss'):
            setattr(self, _prefix+'FileListBoxFrame', ttk.Frame(
                self.FileListBoxFrame, height = 500, width = 1000))
            getattr(self, _prefix+'FileListBoxFrame').pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrolls[_prefix+'yScroll']=ttk.Scrollbar(
                getattr(self, _prefix+'FileListBoxFrame'), orient=tk.VERTICAL)
            scrolls[_prefix+'yScroll'].pack(side=styles[_prefix][0], fill=tk.Y)
            scrolls[_prefix+'xScroll']=ttk.Scrollbar(
                getattr(self, _prefix+'FileListBoxFrame'), orient=tk.HORIZONTAL)
            scrolls[_prefix+'xScroll'].pack(side=tk.BOTTOM, fill=tk.X)
            setattr(self, _prefix+'filelist', tk.StringVar())

            setattr(self, _prefix+'FileListBox', tk.Listbox(
                getattr(self, _prefix+'FileListBoxFrame'),
                                      listvariable=getattr(self, _prefix+'filelist'),
                                      selectmode=tk.EXTENDED,
                                      height = 20, width = 45, relief=tk.RAISED, bd=1,
                                      bg=styles[_prefix][1],
                                      cursor=styles[_prefix][2],
                                      #font=Font(size=10),
                                      xscrollcommand=scrolls[_prefix+'xScroll'].set,
                                      yscrollcommand=scrolls[_prefix+'yScroll'].set,
                                      highlightcolor=cl.LIGHTBLUE,
                                      highlightbackground=cl.GREY,
                                      activestyle='none',
                                        )
                                      )

            getattr(self, _prefix+'FileListBox').bind('<<ListboxSelect>>', getattr(self, _prefix+'ListBoxClick'))
            scrolls[_prefix+'xScroll']['command'] = getattr(self, _prefix+'FileListBox').xview
            scrolls[_prefix+'yScroll']['command'] = getattr(self, _prefix+'FileListBox').yview
            getattr(self, _prefix+'FileListBox').pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.master.bind('<Left>', self.KeepFileClick)
        self.master.bind('<Right>', self.TossFileClick)
        self.master.bind('<Up>', self.ListBoxUp)
        self.master.bind('<Down>', self.ListBoxDown)

    def QuitClick(self):
        self.alive.clear()
        print("Quitting...")
        self.Quit()

    def KeepListBoxClick(self, event): #pylint: disable=unused-argument
        self.keeptoss = 'Keep'
        self.__ListBoxClick('Keep')

    def TossListBoxClick(self, event): #pylint: disable=unused-argument
        self.keeptoss = 'Toss'
        self.__ListBoxClick('Toss')

    def __ListBoxClick(self, _prefix):
        selected = [getattr(self, _prefix+'FileListBox').get(x).replace("_"," ")
                for x in getattr(self, _prefix+'FileListBox').curselection()]
        if len(selected) == 1:
            self.DisplayDataFigure(_prefix, selected[-1])
        elif len(selected) > 1:
            self.DisplayDataFigures(_prefix, selected)
    
        
    def GuessClick(self):
        if not hasattr(self, 'selection_cache'):
            self.logger.error("No files loaded")
            self.handler.flush()
            return
        if not self.all_files_parsed:
            self.logger.error("Wait for parser to complete")
            return
        self.child_threads.append({'thread':threading.Thread(target=self.doGuess),
                                    'widgets':[self.ButtonGuess, #pylint: disable=no-member
                                               self.ButtonParse, #pylint: disable=no-member
                                               self.KeepFileListBox, #pylint: disable=no-member
                                               self.TossFileListBox]}) #pylint: disable=no-member
        self.child_threads[-1]['thread'].name = 'Plateaux Guesser'
        self.child_threads[-1]['thread'].start()
        
    def doGuess(self):
        self.logger.info("Starting search for plateaux...")
        guessQ = queue.Queue()
        for fn in self.selection_cache['Keep_files']:
            _fn = os.path.join(self.indir, fn)
            guessQ.put((fn, self.ivs_files[_fn]['d'], self.ivs_files[_fn]['I']))
            
        children = []
        for _ in range(0,8):
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
                                   'widgets':[self.ButtonParse,  #pylint: disable=no-member
                                              self.KeepFileListBox,  #pylint: disable=no-member
                                              self.TossFileListBox]}) #pylint: disable=no-member
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
                                    'widgets':[self.ButtonGuess, #pylint: disable=no-member
                                               self.ButtonReset, #pylint: disable=no-member
                                               self.ButtonArchiveTossed]}) #pylint: disable=no-member
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
        if self.child_threads:
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
        if not self.selection_cache['Toss_files']:
            self.logger.info("No files to toss.")
            return
        archive_dir = os.path.join(self.indir, 'TossedArchive')
        if not os.path.exists(archive_dir):
            os.mkdir(archive_dir)
        while self.selection_cache['Toss_files']:
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

    def KeepFileClick(self, event=None): #pylint: disable=unused-argument
        self.__FileClick('Toss', 'Keep')
        
    def TossFileClick(self, event=None): #pylint: disable=unused-argument
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

    def ListBoxUp(self, event=None): #pylint: disable=unused-argument
        self.__listbox_increment(self.keeptoss, 1)

    def ListBoxDown(self, event=None): #pylint: disable=unused-argument
        self.__listbox_increment(self.keeptoss, -1)

    def __listbox_increment(self, _prefix, moveby):
        '''
        A hack to re-bind up/down arrow keys to listboxes when matplotlib steals focus.
        '''
        selected = getattr(self, _prefix+'FileListBox').curselection()
        if not selected:
            return
        idx = selected[0] - moveby
        if 0 <= idx <= len(getattr(self, _prefix+'FileListBox').get(0, tk.END)):
            print("Incrementing %sFileLisBox by %s" % (_prefix, moveby))
            getattr(self, _prefix+'FileListBox').activate(idx)
            getattr(self, _prefix+'FileListBox').selection_clear(0,tk.END)
            getattr(self, _prefix+'FileListBox').selection_set(idx)
            getattr(self, _prefix+'FileListBox').see(idx)
            getattr(self, _prefix+'ListBoxClick')(_prefix)

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
        self.DisplayHistogramData('Keep', Ghist)
        self.clearplot('Toss')
        Ghistwriter(self.logger, self.outdir, Ghist)

    def clearplot(self, label):
        if getattr(self, label+'PlotCanvas') is not None:
            getattr(self, label+'PlotCanvas').destroy()
        if getattr(self, label+'ToolBar') is not None:
            getattr(self, label+'ToolBar').destroy()
        setattr(self, label+'PlotCanvas', None)
        setattr(self, label+'ToolBar', None)

    def __update_plot_canvas(self, canvas, toolbar, label):
        self.clearplot(label)
        toolbar.pack(side=tk.BOTTOM, expand=False)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        setattr(self, label+'PlotCanvas', canvas)
        setattr(self, label+'ToolBar', toolbar)

    def DisplayHistogramData(self, label, hist):
        labels={'title':'G Histogram',
        'X': 'G/G0',
        'Y': 'Frequency'}
        canvas, toolbar = getHistplot(
                    getattr(self, label+'CanvasFrame'),
                    hist.fits['bins'], 
                    hist.fits['freq'],
                    hist.fits['fit'],
                    labels)
        self.__update_plot_canvas(canvas, toolbar, label)

    
    def DisplayDataFigure(self, label, fn):
        fn = os.path.join(self.indir, fn)
        self.ivs_files.AddFile(fn)
        self.handler.flush()      
        labels={'title':os.path.basename(fn),
                'X': 'distance',
                'Y': 'current'}

        canvas, toolbar = getXYplot(
                    getattr(self, label+'CanvasFrame'),
                    self.ivs_files[fn]['d'],                       
                    self.ivs_files[fn]['I'],
                    labels)
        self.__update_plot_canvas(canvas, toolbar, label)

        

    def DisplayDataFigures(self, label, fns):
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

        canvas, toolbar = getXYZplot(
                    getattr(self, label+'CanvasFrame'),
                    X, Y, labels)
        self.__update_plot_canvas(canvas, toolbar, label)
