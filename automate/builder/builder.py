import logging
import os
import shutil
from pathlib import Path
from typing import Union

from patchwork.transfers import rsync

from .. import compiler


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

        self.logger = logging.getLogger(__name__)

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
    def configure(self, c, cmake_definitions=[]):
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

        definitions = " ".join(["-D{}".format(d) for d in cmake_definitions])

        with c.cd(str(self.builddir)):
            command = "cmake -DCMAKE_BUILD_TYPE='RelWithDebugInfo' -DCMAKE_TOOLCHAIN_FILE=toolchain.cmake {} {}".format(
                self.srcdir, definitions
            )
            self.logger.info("Running cmake: {}".format(command))
            c.run(command)

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
                source=str(self.builddir / "install") + "/",
                target=str(self.prefix),
                delete=delete,
                rsync_opts="-l",
            )


class KernelBuilder(BaseBuilder):
    def _kernel_desc(self, kernel_id):
        board = self.cc.board

        kernel_desc = None
        for kernel in board.os.kernels:
            if kernel.id == kernel_id:
                kernel_desc = kernel
                break

        if kernel_desc is None:
            raise Exception(
                "Could not find config with id: {} for board {}".format(
                    kernel_id, board.id
                )
            )

        return kernel_desc

    def _arch(self):
        arch = (
            self.cc.machine.value
            if self.cc.machine.value != "aarch64"
            else "arm64"
        )
        return arch

    def _cross_compile(self):
        cross_compile = os.path.join(self.cc.bin_path, self.cc.prefix)

        return cross_compile

    def configure(self, c, kernel_id, config_options=[]):
        self._mkbuilddir()
        kernel_desc = self._kernel_desc(kernel_id)

        with c.cd(str(self.builddir)):
            srcdir = self.builddir / kernel_desc.kernel_srcdir

            if not Path(srcdir).exists():
                c.run("cp {} .".format(kernel_desc.kernel_source))
                kernel_archive = Path(kernel_desc.kernel_source).name
                c.run("tar xvjf {}".format(str(kernel_archive)))

            with c.cd(str(srcdir)):

                c.run("cp {} .config".format(kernel_desc.kernel_config))

                c.run(
                    "make ARCH={0} CROSS_COMPILE={1} oldconfig".format(
                        self._arch(), self._cross_compile()
                    )
                )

                config_fragment = srcdir / ".config_fragment"
                with config_fragment.open("w") as fragment:
                    for config_option in config_options:
                        fragment.write(config_option)
                        fragment.write("\n")

                with c.prefix(
                    "export ARCH={0} && export CROSS_COMPILE={1}".format(
                        self._arch(), self._cross_compile()
                    )
                ):
                    c.run(
                        "./scripts/kconfig/merge_config.sh .config .config_fragment"
                    )

                c.run("cp .config {}".format(kernel_desc.kernel_config))

    def build(self, c, kernel_id):
        self._mkbuilddir()
        kernel_desc = self._kernel_desc(kernel_id)

        with c.cd(str(self.builddir)):
            srcdir = kernel_desc.kernel_srcdir
            with c.cd(str(srcdir)):
                c.run(
                    "make ARCH={0} CROSS_COMPILE={1}".format(
                        self._arch(), self._cross_compile()
                    )
                )


class MakefileBuilder(BaseBuilder):
    # TODO: implement Makefile Builder
    pass


class SPECBuilder(BaseBuilder):
    # TODO: implement spec Builder
    pass


class AutotoolsBuilder(BaseBuilder):
    # TODO: implement autotools builder
    pass
