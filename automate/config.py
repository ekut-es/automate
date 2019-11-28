import configparser
import logging.config
import coloredlogs
import os
import ruamel.yaml as yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union

from .model import ConfigModel

_search_paths = [
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "config.yml"),
    "~/.der_schrank/config.yml"]


def _configure_automate(base_dir: Union[Path, str], automate_conf: Dict[str, Any]) -> ConfigModel:
    base_dir = Path(base_dir).resolve()
    config_model = ConfigModel(**automate_conf)

    model_dict = config_model.dict()

    for key, item in model_dict.items():
        if isinstance(item, Path):
            item = item.expanduser()
            if not item.is_absolute():
                item = base_dir / item
            item = item.resolve()

            model_dict[key] = item

    config_model = ConfigModel(**model_dict)

    logging.info("Using configuration:")
    for key, item in config_model.dict().items():
        logging.info("  {}: {}".format(key, item))

    return config_model


def _configure_logging(logging_conf: Dict[str, Any]) -> None:
    level = logging_conf["level"] if "level" in logging_conf else "DEBUG"
    fmt = logging_conf["fmt"] if "fmt" in logging_conf else "%(message)s"
    coloredlogs.install(level=level, fmt=fmt)


def configure(config_file: Optional[str] = None) -> ConfigModel:

    if config_file is None:
        for path in _search_paths:
            path = os.path.expanduser(path)
            if not os.path.isabs(path):
                path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    path)
            if os.path.exists(path):
                config_file = path
                break

    if config_file is None:
        raise Exception("Could not find configuration file in {}".format(
            " ".join(_search_paths)))

    if os.path.exists(config_file):
        with open(config_file, "r") as cf:
            config_yaml = yaml.load(cf, Loader=yaml.Loader)

            _configure_logging(config_yaml['logging'])
            config_model = _configure_automate(os.path.dirname(config_file),
                                               config_yaml['automate'])
            config = config_model

            return config_model

    raise Exception("Could not find configuration file in {}".format(
        " ".join(_search_paths)))
