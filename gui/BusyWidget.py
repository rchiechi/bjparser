#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 09:13:15 2019

@author: rchiechi
"""

from random import randint

class BusyWidget:
    
    animate = False
    x1 = 10
    y1 = 10
    x2 = 30
    y2 = 60
    
    
    def __init__(self, canvas):
        self.canvas = canvas
        self.ball = canvas.create_oval(self.x1, self.y1, self.x2, self.y2, fill="red")


    def Busy(self):
        self.canvas.delete("all")
        self.animate = True
        self.move_ball()
    
    def Free(self):
        self.animate = False
        self.canvas.delete("all")


    def move_ball(self):
        deltax = randint(0,5)
        deltay = randint(0,5)
        self.canvas.move(self.ball, deltax, deltay)
        if self.animate:
            self.canvas.after(50, self.move_ball)