from .config import Config

import json
import os
import sys

class ConfigManager:
    path_cfg = "cfg.cfg"

    def __init__(self, logger):
        self.logger = logger

    def load(self):
        if os.path.exists(self.path_cfg):
            try:
                with open(self.path_cfg) as f:
                    cfg = json.load(f)
                    self.logger.debug(f"Loaded config: {cfg}")

                    return cfg
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
                return {}
        else:
            self.logger.debug(f"No existing config")
            return {}

    def save(self, cfg):
        try:
            with open(self.path_cfg, 'w') as f:
                json.dump(cfg, f)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save config. Received=[{cfg}]. Error=[{e}]")
            return False

