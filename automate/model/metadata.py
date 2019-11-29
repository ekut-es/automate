from pydantic import BaseModel, Schema
from enum import Enum
from typing import List, Dict, Any


from .compiler import CompilerModel
from .board import BoardModel
from .model_base import *


class MetadataModel(DataModelBase):
    compilers: List[CompilerModel]
    boards: List[BoardModel]

    def get_board(self, board_id: str) -> BoardModel:
        board = None
        for candidate_board in self.boards:
            if board_id == candidate_board.id:
                board = candidate_board
                break

        if board is None:
            raise Exception("Could not find board {}".format(board_id))

        return board

    def get_compiler(self, compiler_id: str) -> CompilerModel:
        compiler = None
        for candidate in self.compilers:
            if compiler_id == candidate.id:
                compiler = candidate
                break

        if compiler is None:
            raise Exception("Could not find compiler {}".format(compiler_id))

        return compiler
