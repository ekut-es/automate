import logging
import shlex
import subprocess
from pathlib import Path
from typing import List, Union

from . import board
from .builder import BaseBuilder, CMakeBuilder, KernelBuilder, MakefileBuilder
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
        """ List of supported triples """
        return self.model.triples

    @property
    def version(self) -> str:
        """Compiler version"""
        return self.model.version

    @property
    def multiarch(self) -> bool:
        """Wether this compiler supports multiarch rootfs"""
        return self.model.multiarch

    @property
    def basedir(self) -> Path:
        return Path(self.model.basedir)

    @property
    def bin_path(self) -> Path:
        """Installation path of compiler tools"""
        return Path(self.model.basedir) / "bin"

    @property
    def prefix(self):
        """Prefix of compiler tools eg: arm-linux-gnueabihf"""
        return self.model.prefix

    @property
    def cc(self) -> str:
        """Binary name of C compiler"""
        return self.model.prefix + self.model.cc

    @property
    def cxx(self) -> str:
        """Binary name of C++ compiler"""
        return self.model.prefix + self.model.cxx

    @property
    def asm(self) -> str:
        """Binary name of assembler"""
        return self.model.prefix + self.model.asm

    @property
    def ld(self) -> str:
        """Binary name of Linker"""
        return self.model.prefix + self.model.ld

    @property
    def toolchain(self) -> Toolchain:
        """Toolchain family of the compiler eg. LLVM or GCC"""
        return self.model.toolchain

    @property
    def id(self) -> str:
        """Unique identifier of compiler in metadata"""
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
        # self.opt_flags = "-O2"
        self.opt_flags = ""

    @property
    def gcc_toolchain(self) -> Union[None, "CrossCompiler"]:
        """GCC toolchain to use for LLVM based cross compilers

        The gcc toolchain is used to provide the linker, 
        and the runtime libraries libgcc and libstdc++
        """
        if self.toolchain == Toolchain.LLVM:
            return self.board.compiler(toolchain=Toolchain.GCC)
        return None

    @property
    def os(self) -> OS:
        """OS part of compiler target triple"""
        os = self.board.os.triple.os
        assert isinstance(os, OS)
        return os

    @property
    def machine(self) -> Machine:
        """Machine part of compiler target triple"""
        m = self.board.os.triple.machine
        assert isinstance(m, Machine)
        return m

    @property
    def environment(self) -> Environment:
        """Environment part of compiler target triple"""
        e = self.board.os.triple.environment
        assert isinstance(e, Environment)
        return e

    @property
    def isa_flags(self) -> str:
        """Default isa specific flags for this board"""
        isa = self.board.cores[self.core].isa
        return self.model.isa_map.get(isa, "")

    @property
    def uarch_flags(self) -> str:
        """Default microarchitecture specific flags for this board"""
        uarch = self.board.cores[self.core].uarch
        ret = self.model.uarch_map.get(uarch, "")
        return str(ret)

    @property
    def uarch_or_isa_flags(self) -> str:
        """Default flags machine specific flags for this board"""
        core = self.board.cores[self.core]
        flag = self.uarch_flags
        if not flag:
            flag = self.isa_flags

        return flag

    @property
    def sysroot(self) -> Union[Path, str]:
        """Sysroot flag for this compiler"""
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
        """Boolean flag wether this compiler is expected to generate working executables
        """
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
        """basic flags shared between  C/C++ compiler and Linker
        """
        flags = []

        if self.toolchain == Toolchain.LLVM:
            assert self.gcc_toolchain is not None
            flags.append(f"--gcc-toolchain={self.gcc_toolchain.basedir}")
            flags.append(f"-ccc-gcc-name {self.gcc_toolchain.cc}")
            flags.append("--rtlib=libgcc")
            flags.append("--stdlib=libstdc++")
            os_triple = self.board.os.triple
            flags.append(
                f"-target {os_triple.machine.value}-{os_triple.os.value}-{os_triple.environment.value}"
            )

        if self.uarch_or_isa_flags:
            flags.append(self.uarch_or_isa_flags)

        if self.sysroot:
            flags.append("--sysroot={}".format(self.sysroot))
        else:
            if self.toolchain == Toolchain.LLVM:
                assert self.gcc_toolchain is not None
                command = f'"{self.gcc_toolchain.bin_path}/{self.gcc_toolchain.cc}" -print-sysroot'

                p = subprocess.Popen(
                    shlex.split(command),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                )

                stdout, stderr = p.communicate()
                stdout_dec = stdout.decode("utf-8")
                sysroot = stdout_dec.strip()
                flags.append(f"--sysroot={sysroot}")

        return " ".join(flags)

    @property
    def cflags(self) -> str:
        """CFLAGS for this compiler
        """
        flags = []

        if self.opt_flags:
            flags.append(self.opt_flags)

        base_flags = self.base_flags
        if base_flags:
            flags.append(base_flags)

        return " ".join(flags)

    @property
    def cxxflags(self) -> str:
        """CXXFLAGS for this compiler
        """
        return self.cflags

    @property
    def ldflags(self):
        """LDFLAGS for this compiler
        
        These flags are appended to the linker commandline before object files
        """
        flags = []

        base_flags = self.base_flags
        if self.base_flags:
            flags.append(self.base_flags)

        return " ".join(flags)

    @property
    def libs(self) -> str:
        """LIBFLAGS for this compiler 

        These flags are appended to the linker driver commandline after the objectfiles
        Currently not used
        """

        return ""

    def _system_includes(self) -> List[str]:
        """ TODO: remove """
        if self.toolchain == Toolchain.LLVM:
            assert self.gcc_toolchain is not None
            return self.gcc_toolchain._system_includes()
        includes = []

        command = f'"{self.bin_path}/{self.cc}" {self.cflags} -E -Wp,-v -'

        p = subprocess.Popen(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )

        stdout, stderr = p.communicate("".encode("utf-8"))
        stderr_dec = stderr.decode("utf-8")
        for line in stderr_dec.split("\n"):
            line = line.strip()
            if line.startswith("/"):
                includes.append(line)
        return includes

    def builder(self, typ, *args, **kwargs) -> BaseBuilder:
        """ Return a builder object for this compiler

        # Arguments
        typ: Type of the buildsystem to use choices are cmake, kernel, make
        *args: positional arguments for Builder.__init__
        **kwargs: keyword arguments for Builder.__init__
        
        # Returns
        configured builder object
        """

        if typ == "cmake":
            return CMakeBuilder(self, *args, **kwargs)
        elif typ == "kernel":
            return KernelBuilder(self, *args, **kwargs)
        elif typ == "make":
            return MakefileBuilder(self, *args, **kwargs)

        raise Exception("Could not find builder {}".format(typ))

    @property
    def default_builddir(self) -> Path:
        """ The default build directory for this cross compiler / board combinarion 
            For now this is just "<cwd>/builds/<board_id>"
        """
        return Path("builds") / str(self.board.id)
