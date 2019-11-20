import logging
from glob import glob
import ruamel.yaml as yaml

from .model import CompilerModel, LoadedCompilerModel, DataModel, LoadedBoardModel

from .config import configure


class ModelLoader(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = configure()
        logging.debug("Metadata Loader for {}".format(self.config.metadata))

        self.model = None

    def load_compilers(self):
        compiler_files = glob(self.config.metadata +
                              "/compilers/**/description.yml", recursive=True)
        compilers = []
        for comp_file in compiler_files:
            logging.info(
                "Loading compiler description from {}".format(comp_file))
            with open(comp_file) as f:
                comp_yaml = yaml.load(f, yaml.RoundTripLoader)
                comp_model = LoadedCompilerModel(
                    model_file=comp_file, **comp_yaml)

            compilers.append(comp_model)

        return compilers

    def load_boards(self):

        boards = []
        for board_file in glob(self.config.metadata+"/boards/**/description.yml", recursive=True):
            logging.info(
                "Loading board description from {}".format(board_file))

            with open(board_file) as f:
                yaml_file = yaml.load(f, yaml.RoundTripLoader)
                board_model = LoadedBoardModel(
                    model_file=board_file, **yaml_file)
                boards.append(board_model)

        return boards

    def load_model(self):
        compilers = self.load_compilers()
        boards = self.load_boards()
