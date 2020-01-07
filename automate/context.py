import os.path

import invoke

from .board import Board
from .compiler import Compiler
from .config import AutomateConfig
from .loader import ModelLoader


class AutomateContext(invoke.Context):
    def __init__(self, config: AutomateConfig):
        super(AutomateContext, self).__init__(config)

        loader = ModelLoader(config)
        self.metadata = loader.load()

    def boards(self):
        for board in self.metadata.boards:
            yield Board(
                board,
                self.metadata.compilers,
                os.path.expanduser(self.config.automate.identity),
            )

    def board(self, board_id: str) -> Board:
        for board in self.metadata.boards:
            if board.id == board_id:
                return Board(
                    board,
                    self.metadata.compilers,
                    os.path.expanduser(self.config.automate.identity),
                )

        raise Exception(
            "Could not find board {} available boards {}".format(
                board_id, ",".join([board.id for board in self.metadata.boards])
            )
        )

    def compilers(self):
        for compiler in self.metadata.compilers:
            yield Compiler(compiler)

    def compiler(self, compiler_id: str) -> Compiler:

        for compiler in self.metadata.compilers:
            if compiler.id == compiler_id:
                return Compiler(compiler)

        raise Exception(
            "Could not find compiler {} available compilers {}".format(
                compiler_id,
                ",".join([compiler.id for compiler in self.metadata.compilers]),
            )
        )
