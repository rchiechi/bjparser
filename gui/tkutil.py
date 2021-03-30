'''
Utiltiy functions
'''

import os
import platform

_ALL_=['get_widget_under_mouse', 'bring_to_front']

def get_widget_under_mouse(root):
    x,y = root.winfo_pointerxy()
    widget = root.winfo_containing(x,y)
    return widget
    #  print("widget:", widget)
    # root.after(1000, get_widget_under_mouse, root)

def bring_to_front(root):
    if platform.system() == "Darwin":
        os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')#pylint: disable=line-too-long
    else:
        root.master.attributes('-topmost', 1)
        root.master.attributes('-topmost', 0)