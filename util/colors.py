#!/usr/bin/python3

__all__ = ["YELLOW", "WHITE", "RED", "TEAL", "GREEN", "BLUE", "RS"]

try:
    import colorama as cm
except ImportError:
    import sys
    print('Error importing colorama module (try pip3 install colorama)')
    sys.exit()

# Setup colors
cm.init(autoreset=True)
YELLOW=cm.Fore.YELLOW
WHITE=cm.Fore.WHITE
RED=cm.Fore.RED
TEAL=cm.Fore.CYAN
GREEN=cm.Fore.GREEN
BLUE=cm.Fore.BLUE
RS=cm.Style.RESET_ALL

#YELLOW="\033[1;33m"
#WHITE="\033[0m"
#RED="\033[1;31m"
#TEAL="\033[1;36m"
#GREEN="\033[1;32m"
#BLUE="\033[1;34m"
#RS="\033[0m"
#CL="\033[2K"
