from src.gui import GUI

import logging, logging.handlers
import os
import sys

def init_logger():
    if not os.path.isdir("logs"):
        os.mkdir("logs")

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s %(message)s','%m-%d %H:%M:%S')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(logging.WARNING)
    if (debug):
        stdout_handler.setLevel(logging.DEBUG)
    logger.addHandler(stdout_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        "logs/log", maxBytes=(1048576*5), backupCount=0
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    return logger

if __name__ == "__main__":
    debug = False
    if "-d" in sys.argv:
        debug = True
    
    gui = GUI(init_logger())