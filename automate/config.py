import os
from pathlib import Path
from typing import Any, Dict, Optional

from invoke.config import Config, merge_dicts


class AutomateConfig(Config):
    """Encapsulates ~/.automate.yml"""

    prefix = "automate"
    env_prefix = "AUTOMATE"

    @staticmethod
    def global_defaults() -> Any:
        their_defaults = Config.global_defaults()

        my_defaults = {
            "automate": {
                "metadata": os.path.expanduser("~/.automate/metadata"),
                "metadata_url": "git@atreus.informatik.uni-tuebingen.de:ties/timing/schrank/metadata.git",
                "metadata_ref": "main",
                "identity": os.path.expanduser("~/.ssh/id_rsa"),
                "toolroot": os.path.expanduser("~/.automate/tools"),
                "boardroot": os.path.expanduser("~/.automate/boards"),
            },
            "debug": {"level": "INFO"},
            "tasks": {"collection_name": "autofile"},
        }

        return merge_dicts(their_defaults, my_defaults)
