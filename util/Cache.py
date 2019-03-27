#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 14:13:37 2019

@author: rchiechi
"""


import os
import time
import json

CACHEFILE = os.path.join(os.environ['HOME'], ".cache/STMBJParse.cache")

class Cache():
    
    def __init__(self, logger, cache_file=CACHEFILE):
        self.logger = logger
        self.cache_file = cache_file
        self.__read_cache()
        if 'time_stamp' not in self.cache:
            self.cache['time_stamp'] = time.time()
    
        for _k in ('files_transfered'):
            if _k not in self.cache:
                self.cache[_k] = []
        self.__write_cache()

    def __contains__(self, key):
        return bool(key in self.cache)
        
    def __delitem__(self, key):
        self.cache = self.getCache(None)
        del(self.cache[key])
        self.__write_cache()
        
    def __getitem__(self,key):
        if key not in self:
            self[key] = None
        return self.cache[key]
    
    def __setitem__(self, key, val):
        self.cache[key] = val
        self.__write_cache()
    
    def append(self, key, val):
        self.cache[key].appepnd(val)
        self.__write_cache()
    
    def __read_cache(self):
        
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as fh:
                self.cache = json.load(fh)
            self.logger.debug("Read cache from %s", self.cache_file)
        else:
            self.cache = dict()
            self.logger.debug("No cache found at %s", self.cache_file)
               
    def __write_cache(self):
        
        self.logger.debug("Writing cache to %s", self.cache_file)
        with open(self.cache_file, 'w') as fh:
            json.dump(self.cache, fh)           
