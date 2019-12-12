import logging
from pathlib import Path
from typing import List, Union

from . import board
from .builder import (
    AutotoolsBuilder,
    BaseBuilder,
    CMakeBuilder,
    KernelBuilder,
    MakefileBuilder,
    SPECBuilder,
)
from .model import (
    BoardModel,
    CompilerModel,
    CoreModel,
    MetadataModel,
    TripleModel,
)
from .model.common import (
    ISA,
    OS,
    Environment,
    Machine,
    Toolchain,
    UArch,
    Vendor,
)


class Compiler(object):
    """Represents an unconfigured generic compiler"""

    def __init__(self, compiler: CompilerModel):
        self.model = compiler

    @property
    def triples(self) -> List[TripleModel]:
        return self.model.triples

    @property
    def version(self) -> str:
        return self.model.version

    @property
    def multiarch(self) -> bool:
        return self.model.multiarch

    @property
    def bin_path(self) -> Path:
        return Path(self.model.basedir) / "bin"

    @property
    def prefix(self):
        return self.model.prefix

    @property
    def cc(self) -> str:
        return self.model.prefix + self.model.cc

    @property
    def cxx(self) -> str:
        return self.model.prefix + self.model.cxx

    @property
    def asm(self) -> str:
        return self.model.prefix + self.model.asm

    @property
    def ld(self) -> str:
        return self.model.prefix + self.model.ld

    @property
    def toolchain(self) -> Toolchain:
        return self.model.toolchain

    @property
    def id(self) -> str:
        return self.model.id


class CrossCompiler(Compiler):
    """Represents a Compiler with board specific configuration"""

    def __init__(self, compiler: CompilerModel, board: "board.Board") -> None:
        super(CrossCompiler, self).__init__(compiler)

        self.logger = logging.getLogger(__name__)
        self.board = board

        self.logger.debug(
            "Getting compiler {} for {}".format(compiler.id, board.id)
        )
        self.check_multiarch = True
        self.core = 0
        self.opt_flags = "-O2"

    @property
    def os(self) -> OS:
        os = self.board.os.triple.os
        assert isinstance(os, OS)
        return os

    @property
    def machine(self) -> Machine:
        m = self.board.os.triple.machine
        assert isinstance(m, Machine)
        return m

    @property
    def environment(self) -> Environment:
        e = self.board.os.triple.environment
        assert isinstance(e, Environment)
        return e

    @property
    def isa_flags(self) -> str:
        isa = self.board.cores[self.core].isa
        return self.model.isa_map.get(isa, "")

    @property
    def uarch_flags(self) -> str:
        uarch = self.board.cores[self.core].uarch
        ret = self.model.uarch_map.get(uarch, "")
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

        for ct in self.model.triples:
            if os_triple == (ct.os, ct.machine, ct.environment):
                if self.check_multiarch and self.board.os.multiarch:
                    if not self.model.multiarch:
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
    def cxxflags(self) -> str:
        return self.cflags

    @property
    def ldflags(self):
        flags = []

        base_flags = self.base_flags
        if self.base_flags:
            flags.append(self.base_flags)

        return " ".join(flags)

    def builder(self, typ, *args, **kwargs) -> BaseBuilder:
        if typ == "cmake":
            return CMakeBuilder(self, *args, **kwargs)
        elif typ == "kernel":
            return KernelBuilder(self, *args, **kwargs)
        elif typ == "make":
            return MakefileBuilder(self, *args, **kwargs)
        elif typ == "spec":
            return SPECBuilder(self, *args, **kwargs)
        elif typ == "autotools":
            return AutotoolsBuilder(self, *args, **kwargs)

        raise Exception("Could not find builder {}".format(typ))

    @property
    def default_builddir(self):
        return "build-{}".format(self.board.id)
