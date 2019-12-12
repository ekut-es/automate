from .. import compiler
from pathlib import Path
import shutil

from typing import Union
from patchwork.transfers import rsync


class BaseBuilder(object):
    def __init__(
        self,
        cc: "compiler.CrossCompiler",
        builddir: Union[Path, str] = "",
        srcdir: Union[Path, str] = "",
        prefix: Union[Path, str] = "",
    ):
        self.cc = cc

        if builddir:
            self.builddir = Path(builddir)
        else:
            self.builddir = Path(cc.default_builddir)
        if srcdir:
            self.srcdir = Path(srcdir)
        else:
            self.srcdir = Path(".")

        if prefix:
            self.prefix = Path(prefix)
        else:
            self.prefix = Path(cc.board.rundir)

        self.prefix = self.prefix.absolute()
        self.srcdir = self.srcdir.absolute()
        self.builddir = self.builddir.absolute()

    def configure(self, c):
        "Configure the build"

        raise NotImplemented("Configure is not implemented")

    def build(self, c):
        "Build target code"
        raise NotImplemented("Build is not implemented")

    def install(self, c):
        "Installs the built binaries on the board"
        raise NotImplemented("Installation is not implemented")

    def clean(self, c):
        "Removes the builddir"
        if self.builddir != self.srcdir:
            if self.builddir.exists():
                shutil.rmtree(self.builddir)

    def _mkbuilddir(self):
        "Creates the build directory"
        self.builddir.mkdir(parents=True, exist_ok=True)


class CMakeBuilder(BaseBuilder):
    def configure(self, c):
        self._mkbuilddir()

        toolchain_file = self.builddir / "toolchain.cmake"
        with toolchain_file.open("w") as tf:
            tf.write("set(CMAKE_SYSTEM_NAME Linux)\n")
            tf.write(
                "set(CMAKE_SYSTEM_PROCESSOR {})\n".format(self.cc.machine.value)
            )
            tf.write("\n")
            tf.write("set(CMAKE_SYSROOT {})\n".format(self.cc.sysroot))
            tf.write(
                "set(CMAKE_STAGING_PREFIX {})\n".format(
                    self.builddir / "install"
                )
            )
            tf.write("\n")
            tf.write(
                "set(CMAKE_C_COMPILER {}/{})\n".format(
                    self.cc.bin_path, self.cc.cc
                )
            )
            tf.write(
                "set(CMAKE_CXX_COMPILER {}/{})\n".format(
                    self.cc.bin_path, self.cc.cxx
                )
            )
            tf.write("\n")
            tf.write("set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)\n")
            tf.write("set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)\n")
            tf.write("set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)\n")
            tf.write("set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)\n")

        with c.cd(str(self.builddir)):
            c.run(
                "cmake -DCMAKE_BUILD_TYPE='RelWithDebugInfo' -DCMAKE_TOOLCHAIN_FILE=toolchain.cmake {}".format(
                    self.srcdir
                )
            )

    def build(self, c):
        self._mkbuilddir()
        with c.cd(str(self.builddir)):
            c.run("cmake --build  .")

    def install(self, c, delete=False):
        with c.cd(str(self.builddir)):
            c.run("cmake  --build . --target install ")

        with self.cc.board.connect() as con:
            rsync(
                con,
                source=str(self.builddir / "install"),
                target=str(self.prefix),
                delete=delete,
            )


class KernelBuilder(BaseBuilder):
    def configure(self, c):
        self._mkbuilddir()

    def build(self, c, target="all"):
        self._mkbuilddir()


class MakefileBuilder(BaseBuilder):
    # TODO: implement Makefile Builder
    pass


class SPECBuilder(BaseBuilder):
    # TODO: implement spec Builder
    pass


class AutotoolsBuilder(BaseBuilder):
    # TODO: implement autotools builder
    pass
