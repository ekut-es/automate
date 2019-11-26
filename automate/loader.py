import logging
from glob import glob
import os
from datetime import datetime
import ruamel.yaml as yaml

from .model import DataModel

from .config import configure

from typing import List


class ModelLoader(object):
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.config = configure()
        self.logger.debug(
            "Metadata Loader for {}".format(self.config.metadata))

        self.model = None

    def _load_metadata_list(self, pattern, recursive=True):
        res = []
        files = glob(os.path.join(self.config.metadata,
                                  pattern), recursive=recursive)

        for file_name in files:
            self.logger.info("Loading metadata from {}".format(file_name))
            with open(file_name) as f:
                mtime = datetime.utcfromtimestamp(os.path.getmtime(file_name))
                yaml_dict = yaml.load(f, yaml.RoundTripLoader)
                yaml_dict["model_file"] = file_name
                yaml_dict["model_file_mtime"] = mtime
                res.append(yaml_dict)

        return res

    def load_model(self) -> DataModel:
        compiler = self._load_metadata_list("compiler/**/description.yml")
        boards = self._load_metadata_list("boards/**/description.yml")

        return DataModel(compiler=compiler, boards=boards)
