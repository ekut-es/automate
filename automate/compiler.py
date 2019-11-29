import logging

from .model import CompilerModel, BoardModel, MetadataModel


class CrossCompiler(object):
    def __init__(self, compiler: CompilerModel, board: BoardModel) -> None:
        self.logger = logging.getLogger(__name__)
        self.board = board
        self.compiler = compiler

        self.logger.debug(
            "Getting compiler {} for {}".format(compiler.id, board.id))
        self.check_multiarch = True

    @property
    def valid(self):
        os_triple = (os.triple.os,
                     os.triple.machine,
                     os.triple.environment)
        for ct in compiler.triples:
            if os_triple == (ct.os, ct.machine, ct.environment):
                return True

        return False


class CrossCompilerGenerator(object):
    def __init__(self, metadata: MetadataModel) -> None:
        self.logger = logging.getLogger(__name__)
        self.metadata = metadata

    def get_compiler(self, compiler_id: str, board_id: str):
        self.logger.debug(
            "Getting compiler {} for {}".format(compiler_id, board_id))
        compiler = None
        for candidate in self.metadata.compilers:
            if compiler_id == candidate.id:
                compiler = candidate
                break

        if compiler is None:
            raise Exception("Could not find compiler {}".format(compiler_id))

        board = None
        for candidate_board in self.metadata.boards:
            if board_id == candidate_board.id:
                board = candidate_board
                break

        if board is None:
            raise Exception("Could not find board {}".format(board_id))

        cc = CrossCompiler(compiler, board)
        if cc.valid:
            raise Exception("{} and {} combination is not valid".format(
                compiler_id, board_id))

        return cc
