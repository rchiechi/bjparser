#!/usr/bin/python3
from tkinter import ttk

__all__ = ["TTKSTYLE", "BLACK","YELLOW", "WHITE", "RED", "TEAL", "GREEN", "BLUE", "GREY", "LIGHTRED", "LIGHTBLUE", "LIGHTGREEN"]

BLACK="#000000"
YELLOW="#f4e012"
WHITE="#ffffff"
RED="#ff0000"
TEAL="#78CBFD"
GREEN="#09f218"
BLUE="#090df2"
GREY='#e8e8e8'
LIGHTRED="#ff9999"
LIGHTBLUE="#ccffff"
LIGHTGREEN="#ccfccc"

TTKSTYLE=ttk.Style()
TTKSTYLE.configure('TFrame', background=LIGHTBLUE)
TTKSTYLE.configure('TPanedwindow', sashwidth=10, sashpad=5)
TTKSTYLE.configure('Keep.TFrame', background=LIGHTGREEN)
TTKSTYLE.configure('Toss.TFrame', background=LIGHTRED)

