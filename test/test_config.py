from automate.config import configure
import os
from pathlib import Path

root_path = os.path.dirname(os.path.abspath(__file__))

config_file = os.path.join(root_path,
                           "test_config.yml")


def test_config():
    config = configure(config_file)

    assert config.identity == Path(os.path.join(root_path,
                                                "test_identity"))
    assert config.metadata == Path(os.path.join(root_path,
                                                "test_metadata"))
    assert config.toolroot == Path(os.path.join(root_path,
                                                "test_toolroot"))
    assert config.boardroot == Path(os.path.join(root_path,
                                                 "test_boardroot"))


def test_configure():
    assert configure() is not None
