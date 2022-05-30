from src.gui import GUI
from src.logger import Logger

import sys

if __name__ == "__main__":
    debug = True
    if "-l" in sys.argv:
        debug = False
    
    logger = Logger(debug)
    gui = GUI(logger)