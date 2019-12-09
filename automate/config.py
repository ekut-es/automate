import configparser
import logging.config
import coloredlogs
import os
import ruamel.yaml as yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union

from invoke.config import Config, merge_dicts


class AutomateConfig(Config):
    prefix = "automate"
    env_prefix = "AUTOMATE"

    @staticmethod
    def global_defaults() -> Any:
        their_defaults = Config.global_defaults()

        my_defaults = {
            "automate": {
                "metadata": os.path.expanduser("~/.automate/metadata"),
                "identity": os.path.expanduser("~/.ssh/id_rsa"),
                "toolroot": os.path.expanduser("~/.automate/tools"),
                "boardroot": os.path.expanduser("~/.automate/boards"),
            },
            "debug": {"level": "INFO"},
        }

        return merge_dicts(their_defaults, my_defaults)
