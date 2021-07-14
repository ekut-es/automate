import logging
import shlex
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from . import board
from .model import (
    BoardModel,
    CompilerModel,
    CoreModel,
    MetadataModel,
    TripleModel,
    VersionString,
)
from .model.common import OS, Environment, Machine, Toolchain

if TYPE_CHECKING:
    import automate.context


class Compiler(object):
    """Represents an unconfigured generic compiler"""

    def __init__(
        self,
        context: "automate.context.AutomateContext",
        compiler: CompilerModel,
    ):
        self.model = compiler
        self.context = context
        self.logger = logging.getLogger(__name__)

    @property
    def triples(self) -> List[TripleModel]:
        """ List of supported triples """
        return self.model.triples

    @property
    def version(self) -> VersionString:
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
    def ar(self) -> str:
        """Binary name of Archiver"""
        return self.model.prefix + self.model.ar

    @property
    def toolchain(self) -> Toolchain:
        """Toolchain family of the compiler eg. LLVM or GCC"""
        return self.model.toolchain

    @property
    def id(self) -> str:
        """Unique identifier of compiler in metadata"""
        self.logger.warning("WARNING: this method has been deprecated")
        return self.model.name

    @property
    def name(self) -> str:
        """Unique identifier of compiler in metadata"""
        return self.model.name

    @property
    def runtime(self) -> str:
        return self.model.runtime


class CrossCompiler(Compiler):
    """Represents a Compiler with board specific configuration"""

    def __init__(
        self,
        context: "automate.context.AutomateContext",
        compiler: CompilerModel,
        board: "board.Board",
    ) -> None:
        super(CrossCompiler, self).__init__(context, compiler)

        self.logger = logging.getLogger(__name__)
        self.board = board

        self.logger.debug(
            "Getting compiler {} for {}".format(compiler.name, board.name)
        )
        self.check_multiarch = True
        self.core = 0
        self._flags: List[str] = ["-O2"]
        self._cflags: List[str] = []
        self._cxxflags: List[str] = []
        self._ldflags: List[str] = []
        self._libs: List[str] = []
        self._enable_sysroot = True
        self._isa_opt = True
        self._uarch_opt = True

    def configure_extend(
        self,
        flags: Optional[str] = None,
        cflags: Optional[str] = None,
        cxxflags: Optional[str] = None,
        ldflags: Optional[str] = None,
        libs: Optional[str] = None,
    ) -> None:
        """ Extend compiler flags

        For arguments see configure
        """

        if flags is not None:
            self._flags.extend(shlex.split(flags))

        if cflags is not None:
            self._cflags.extend(shlex.split(cflags))

        if cxxflags is not None:
            self._cxxflags.extend(shlex.split(cxxflags))

        if ldflags is not None:
            self._ldflags.extend(shlex.split(ldflags))

        if libs is not None:
            self._libs.extend(shlex.split(libs))

    def configure(
        self,
        flags: Optional[str] = None,
        cflags: Optional[str] = None,
        cxxflags: Optional[str] = None,
        ldflags: Optional[str] = None,
        libs: Optional[str] = None,
        uarch_opt=True,
        isa_opt=True,
        enable_sysroot=True,
    ) -> None:
        """ Set compiler options

    # Arguments
    flags: Basic flags (used for compilation and linkags)
    cflags: flags for C compiler
    cxxflags: flags for C++ compiler
    ldflags: flags for linker (linker is assumed to call C/C++-Compiler)
    libs: Additional libraries to link (some builds might need -lrt)
    uarch_opt: Enable microarchitecture specific optimizations
    isa_opt: Enable isa specific optimizations
    enable_sysroot: Link and build with --sysroot set to a dump of the boards root file system, linkers and cmake will link to libraries installed on the board
    """

        if flags is not None:
            self._flags = shlex.split(flags)

        if cflags is not None:
            self._cflags = shlex.split(cflags)

        if cxxflags is not None:
            self._cxxflags = shlex.split(cxxflags)

        if ldflags is not None:
            self._ldflags = shlex.split(ldflags)

        if libs is not None:
            self._libs = shlex.split(libs)

        self._isa_opt = isa_opt
        self._uarch_opt = uarch_opt
        self._enable_sysroot = enable_sysroot

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
        """Default isa specific flags for this board if enabled"""

        if not self._isa_opt:
            return ""

        isa = self.board.cores[self.core].isa
        return self.model.isa_map.get(isa, "")

    @property
    def uarch_flags(self) -> str:
        """Default microarchitecture specific flags for this board if enabled"""
        if not self._uarch_opt:
            return ""

        uarch = self.board.cores[self.core].uarch
        ret = self.model.uarch_map.get(uarch, "")
        return str(ret)

    @property
    def uarch_or_isa_flags(self) -> str:
        """Default flags machine specific flags for this board if enabled"""
        core = self.board.cores[self.core]
        flag = self.uarch_flags
        if not flag:
            flag = self.isa_flags

        return flag

    @property
    def features(self) -> List[str]:
        features = self.board.cores[self.core].extensions
        ret = []
        for k, v in self.model.feature_map.items():
            if k in features:
                ret.append(f"+{v}")
            else:
                ret.append(f"-{v}")
        return ret

    @property
    def sysroot(self) -> Union[Path, str]:
        """Sysroot flag for this compiler and board"""
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
            os_triple = self.board.os.triple
            flags.append(
                f"-target {os_triple.machine.value}-{os_triple.os.value}-{os_triple.environment.value}"
            )

        if self.uarch_or_isa_flags:
            flags.append(self.uarch_or_isa_flags)

        if self.sysroot:
            flags.append("--sysroot={}".format(self.sysroot))
        else:
            # Current llvm installations do not find a correct libc
            # so we call die underlying gcc to find its sysroot
            # and set it explicitly
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

        if self._flags:
            flags.extend(self._flags)

        return " ".join(flags)

    @property
    def cflags(self) -> str:
        """CFLAGS for this compiler
        """
        flags = []

        base_flags = self.base_flags
        if base_flags:
            flags.append(base_flags)

        if self._cflags:
            flags.extend(self._cflags)

        return " ".join(flags)

    @property
    def cxxflags(self) -> str:
        """CXXFLAGS for this compiler
        """

        flags = []

        base_flags = self.base_flags
        if base_flags:
            flags.append(base_flags)

        if self.toolchain == Toolchain.LLVM:
            flags.append("--stdlib=libstdc++")

        if self._cxxflags:
            flags.extend(self._cxxflags)

        return " ".join(flags)

    @property
    def ldflags(self):
        """LDFLAGS for this compiler

        These flags are appended to the linker commandline before object files
        """
        flags = []

        base_flags = self.base_flags
        if self.base_flags:
            flags.append(self.base_flags)

        if self.toolchain == Toolchain.LLVM:
            flags.append("--rtlib=libgcc")
            flags.append("--unwindlib=libgcc")
            flags.append("--stdlib=libstdc++")

        if self._ldflags:
            flags.extend(self._ldflags)

        return " ".join(flags)

    @property
    def libs(self) -> str:
        """LIBFLAGS for this compiler

        These flags are appended to the linker driver commandline after the objectfiles
        Currently not used
        """

        libs: List[str] = []

        if self._libs:
            libs.extend(self._libs)

        return " ".join(libs)

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

    @property
    def default_builddir(self) -> Path:
        """ The default build directory for this cross compiler / board combinarion
            For now this is just "<cwd>/builds/<board_id>"
        """
        return Path("builds") / str(self.board.name)

    def __deepcopy__(self, memo) -> "CrossCompiler":
        copy = CrossCompiler(self.context, self.model, self.board)

        copy.check_multiarch = deepcopy(self.check_multiarch, memo)
        copy.core = deepcopy(self.core, memo)
        copy._flags = deepcopy(self._flags, memo)
        copy._cflags = deepcopy(self._cflags, memo)
        copy._cxxflags = deepcopy(self._cxxflags, memo)
        copy._ldflags = deepcopy(self._ldflags, memo)
        copy._libs = deepcopy(self._libs, memo)
        copy._enable_sysroot = deepcopy(self._enable_sysroot, memo)
        copy._isa_opt = deepcopy(self._isa_opt, memo)
        copy._uarch_opt = deepcopy(self._uarch_opt, memo)

        return copy
