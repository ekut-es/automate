from abc import ABC, ABCMeta
from argparse import ArgumentParser
from typing import Dict, Any

from ..loader import get_model
from ..config import configure


class ToolBase(metaclass=ABCMeta):

    def __init__(self):
        self.model = get_model()
        self.config = configure()

    def get_arg_parser(self):
        parser = ArgumentParser(description=self.docstring)

    def parse(self) -> Any:
        parser = self.get_arg_parser()
        return parser.parse()

    def run_cmdline(self):
        arguments = self.parse()
        self.run()

    def run(self) -> int:
        pass
