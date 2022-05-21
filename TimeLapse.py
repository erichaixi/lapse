from src.gui import GUI
from src.logger import Logger

import sys

if __name__ == "__main__":
    debug = False
    if "-d" in sys.argv:
        debug = True
    
    logger = Logger(debug)
    gui = GUI(logger)