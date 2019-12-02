import logging

from typing import List, Union
from pathlib import Path

from .model import (
    CompilerModel,
    BoardModel,
    MetadataModel,
    ConfigModel,
    CoreModel,
)
from .model.common import (
    Toolchain,
    Vendor,
    ISA,
    UArch,
    OS,
    Machine,
    Environment,
    Vendor,
)


class CrossCompiler(object):
    def __init__(self, compiler: CompilerModel, board: BoardModel) -> None:
        self.logger = logging.getLogger(__name__)
        self.board = board
        self.compiler = compiler

        self.logger.debug(
            "Getting compiler {} for {}".format(compiler.id, board.id)
        )
        self.check_multiarch = True
        self.core = 0

    @property
    def opt_flags(self) -> str:
        return "-O2"

    @property
    def id(self) -> str:
        return self.compiler.id

    @property
    def version(self) -> str:
        return self.compiler.version

    @property
    def os(self) -> OS:
        return self.board.os.triple.os

    @property
    def machine(self) -> Machine:
        return self.board.os.triple.machine

    @property
    def environment(self) -> Environment:
        return self.board.os.triple.environment

    @property
    def multiarch(self) -> bool:
        return self.compiler.multiarch

    @property
    def toolchain(self) -> Toolchain:
        return self.compiler.toolchain

    @property
    def bin_path(self) -> Path:
        return Path(self.compiler.basedir) / "bin"

    @property
    def cc(self) -> str:
        return self.compiler.prefix + self.compiler.cc

    @property
    def cxx(self) -> str:
        return self.compiler.prefix + self.compiler.cxx

    @property
    def asm(self) -> str:
        return self.compiler.prefix + self.compiler.asm

    @property
    def ld(self) -> str:
        return self.compiler.prefix + self.compiler.ld

    @property
    def isa_flags(self) -> str:
        isa = self.board.cores[self.core].isa
        return self.compiler.isa_map.get(isa, "")

    @property
    def uarch_flags(self) -> str:
        uarch = self.board.cores[self.core].uarch
        ret = self.compiler.uarch_map.get(uarch, "")
        return str(ret)

    @property
    def uarch_or_isa_flags(self) -> str:
        core = self.board.cores[self.core]
        flag = self.uarch_flags
        if not flag:
            flag = self.isa_flags

        return flag

    @property
    def sysroot(self) -> Union[Path, str]:
        if not Path(self.board.os.sysroot).exists():
            self.logger.warning(
                "Could not find sysroot {} using generic sysroot".format(
                    self.board.os.sysroot
                )
            )
            return ""
        return Path(self.board.os.sysroot)

    @property
    def valid(self) -> bool:
        os_triple = (
            self.board.os.triple.os,
            self.board.os.triple.machine,
            self.board.os.triple.environment,
        )
        for ct in self.compiler.triples:
            if os_triple == (ct.os, ct.machine, ct.environment):
                if self.check_multiarch and self.board.os.multiarch:
                    if not self.compiler.multiarch:
                        return False
                return True

        return False

    @property
    def base_flags(self) -> str:
        flags = []

        if self.uarch_or_isa_flags:
            flags.append(self.uarch_or_isa_flags)

        if self.sysroot:
            flags.append("--sysroot={}".format(self.sysroot))

        return " ".join(flags)

    @property
    def cflags(self) -> str:
        flags = []

        if self.opt_flags:
            flags.append(self.opt_flags)

        base_flags = self.base_flags
        if base_flags:
            flags.append(base_flags)

        return " ".join(flags)

    @property
    def ldflags(self):
        flags = []

        base_flags = self.base_flags
        if self.base_flags:
            flags.append(self.base_flags)

        return " ".join(flags)


class CrossCompilerGenerator(object):
    def __init__(self, metadata: MetadataModel) -> None:
        self.logger = logging.getLogger(__name__)
        self.metadata = metadata

    def get_compiler(self, compiler_id: str, board_id: str) -> CrossCompiler:
        self.logger.debug(
            "Getting compiler {} for {}".format(compiler_id, board_id)
        )

        compiler = self.metadata.get_compiler(compiler_id)
        board = self.metadata.get_board(board_id)

        cc = CrossCompiler(compiler, board)
        if cc.valid:
            raise Exception(
                "{} and {} combination is not valid".format(
                    compiler_id, board_id
                )
            )

        return cc

    def compatible_compilers(self, board_id: str) -> List[CrossCompiler]:
        board = self.metadata.get_board(board_id)

        compilers = []
        for compiler in self.metadata.compilers:
            cc = CrossCompiler(compiler, board)
            if cc.valid:
                compilers.append(cc)

        return compilers

    def get_default_compiler(
        self, board_id: str, toolchain: Toolchain = Toolchain.GCC
    ) -> CrossCompiler:
        """Returns the default compiler for a board, 
           this is currently the newest compatible gcc compiler

           TODO: make default toolchain configurable and/or allow default
           compiler selection using a default toolchain. 
        """

        res = None

        compilers = self.compatible_compilers(board_id)
        compilers_sorted = reversed(sorted(compilers, key=lambda x: x.version))

        for compiler in compilers_sorted:
            if compiler.toolchain == toolchain:
                res = compiler
                break

        if res is None:
            raise Exception("Could not find compiler for {}".format(board_id))

        return res
