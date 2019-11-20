from automate.config import Config, configure
import os


config_ini = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "test_config.ini")


def test_config():
    print("Config ini", config_ini)
    config = Config(config_ini)

    assert config.identity == os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           "test_identity")
    assert config.metadata == os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           "test_metadata")


def test_configure():
    assert configure() is not None
