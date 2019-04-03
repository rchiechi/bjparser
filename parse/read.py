#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 15:43:29 2019

@author: rchiechi
"""

import sys
try:
    import pandas as pd

except ImportError as msg:
    print("\n\t\t> > >%s < < <" % str(msg))
    print("Try pip3 install <module>")
    sys.exit()


class ReadIVS:
    
    def __init__(self, logger, lock, opts):
        self.logger = logger
        self.opts = opts
        self.lock = lock
        self.frames = {}
    
    def __read_file_as_df(self, in_file):
        if in_file in self.frames:
            self.logger.debug('%s already parsed', in_file)
            return
        self.logger.debug('Parsing %s', in_file)
        try:
            df = pd.read_csv(in_file,
                       sep='\t',usecols=(0,1),
                       names=('d','I'),
                       header=105,
                       encoding = "ISO-8859-1")
            df.drop(df.tail(1).index,inplace=True)
        except OSError as msg:
                    self.logger.warn("Skipping %s because %s", in_file ,str(msg))
        with self.lock:
            self.frames[in_file] = df

    def __readfile(self, fileName):
        if fileName in self.frames:
            return
        #TODO Waaaaay too specific to one file format
        distanceData = []
        currentData = []
        with open(fileName, 'rb') as fileData:
            for lines in fileData.readlines()[105:-1]:
                lines = lines.__str__()
                lines = lines[2:-9]
                lines = lines.split('\\t')
                distanceData.append(float(lines[0]))
                currentData.append(float(lines[1]))
        with self.lock:
            self.frames[fileName] = {'d':distanceData, 'I':currentData}
        
  
    def __contains__(self, key):
        return bool(key in self.frames)
        
    def __delitem__(self, key):
        with self.lock:
            del(self.frames[key])
        
    def __getitem__(self, key):
        return self.frames[key]

    def AddFile(self, fn):
        self.KeepFile(fn)
            
    def RemoveFile(self, fn):
        self.TossFile(fn)

    def KeepFile(self, fn):
        self.__readfile(fn)
        
    def TossFile(self, fn):
        with self.lock:
            if fn in self.frames:
                del(self.frames[fn])
        
    def GetFile(self, fn):
        if fn in self.frames:
            return self.frames[fn]
        else:
            return None
    
    def ListFiles(self):
        return list(self.frames.keys())