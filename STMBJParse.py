#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 13:38:59 2019

@author: rchiechi
"""

import argparse
import gui

desc='''
	TBD.
     '''

parser = argparse.ArgumentParser(
     description=desc,formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-L','--loglevel', default='info', choices=('info','warn','error','debug'),
                    help="Set the logging level.")
parser.add_argument('--altparser', default=False, action='store_true',
                    help="Use pandas to parse input files instead if IVS-specific parser.")
parser.add_argument('-e', '--extension', default='ivs',
                    help="Extension of input files to parse.")

opts=parser.parse_args()

# BJParserFrame(opts)

root = gui.MainGUI(opts)
root.mainloop()
