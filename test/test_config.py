from automate.config import Config, configure
import os

root_path = os.path.dirname(os.path.abspath(__file__))

config_file = os.path.join(root_path,
                           "test_config.ini")


def test_config():
    config = Config(config_file)

    assert config.identity == os.path.join(root_path,
                                           "test_identity")
    assert config.metadata == os.path.join(root_path,
                                           "test_metadata")
    assert config.toolroot == os.path.join(root_path,
                                           "test_toolroot")
    assert config.boardroot == os.path.join(root_path,
                                            "test_boardroot")


def test_configure():
    assert configure() is not None
