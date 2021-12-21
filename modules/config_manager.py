from .config import Config

from enum import Enum
import json
import os
import sys

class ConfigError(Enum):
    INVALID_DIR = 1
    LOAD_FAILED = 2

class ConfigManager:
    path_cfg = "cfg.cfg"

    def __init__(self, logger):
        self.logger = logger

    def load(self):
        if os.path.exists(self.path_cfg):
            try:
                with open(self.path_cfg) as f:
                    cfg = Config(json.load(f))

                    return cfg
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
                return Config()
        else:
            self.logger.debug(f"No existing config")
            return Config()

    def save(self, cfg):
        try:
            with open(self.path_cfg, 'w') as f:
                f.write(cfg.toJson())
            return True
        except Exception as e:
            self.logger.error(f"Failed to save config. Received=[{cfg}]. Error=[{e}]")
            return False

