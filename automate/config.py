import configparser
import logging.config
import os

_search_paths = ["../config.ini",
                 "~/.der_schrank/config.ini"]
_config = None


class Config(object):
    def __init__(self, config_file: str) -> None:
        parser = configparser.ConfigParser()
        with open(config_file) as f:
            parser.read_file(f)

        self._config_dir = os.path.dirname(config_file)

        metadata = parser["automate"]["metadata"]
        metadata = self._abspath(metadata)
        self.metadata: str = metadata

        identity = parser["automate"]["identity"]
        identity = self._abspath(identity)
        self.identity: str = identity

        toolroot = parser["automate"]["toolroot"]
        toolroot = self._abspath(toolroot)
        self.toolroot: str = toolroot

        boardroot = parser["automate"]["boardroot"]
        boardroot = self._abspath(boardroot)
        self.boardroot: str = boardroot

        logging.config.fileConfig(parser)

    def _abspath(self, path: str) -> str:
        path = os.path.expanduser(path)
        if not os.path.isabs(path):
            path = os.path.join(self._config_dir,
                                path)
        return path


def configure() -> Config:
    global _config
    if _config is not None:
        return _config

    for path in _search_paths:
        path = os.path.expanduser(path)
        if not os.path.isabs(path):
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                path)
        if os.path.exists(path):
            _config = Config(path)
            return _config

    raise Exception("Could not find configuration file in {}".format(
        " ".join(_search_paths)))
