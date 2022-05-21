import logging
import logging.handlers
import os
import sys

class Logger:
    def __init__(self, debug=False):
        if not os.path.isdir("logs"):
            os.mkdir("logs")

        self.logger = logging.getLogger()
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

        self.logger.setLevel(logging.WARNING)
        if (debug):
            self.logger.setLevel(logging.DEBUG)

        handler = logging.handlers.RotatingFileHandler(
            "logs/log", maxBytes=(1048576*5), backupCount=0
        )
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def debug(self, s):
        self.logger.debug(s)

    def info(self, s):
        self.logger.info(s)

    def warning(self, s):
        self.logger.warning(s)

    def error(self, s):
        self.logger.error(s)