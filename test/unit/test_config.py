import os
from pathlib import Path

import ruamel.yaml as yaml

from automate.config import AutomateConfig

root_path = os.path.dirname(os.path.abspath(__file__))

config_file = os.path.join(root_path, "test_config.yml")


# def test_config():
#
#    with open(config_file) as f:
#        config_dict = yaml.load(config_file, Loader=yaml.Loader)
#
#        config = AutomateConfig(overrides=config_dict, lazy=True)
#
#        assert config.identity == Path(os.path.join(root_path, "test_identity"))
#        assert config.metadata == Path(os.path.join(root_path, "test_metadata"))
#        assert config.toolroot == Path(os.path.join(root_path, "test_toolroot"))
#        assert config.boardroot == Path(
#            os.path.join(root_path, "test_boardroot")
#        )
