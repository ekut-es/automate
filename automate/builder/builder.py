import logging
import os
import shutil
from pathlib import Path
from typing import Union

from .. import compiler
from ..utils.network import rsync


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

        raise NotImplementedError("Configure is not implemented")

    def build(self, c):
        "Build target code"
        raise NotImplementedError("Build is not implemented")

    def install(self, c):
        "Installs the built binaries on the board"
        raise NotImplementedError("Installation is not implemented")

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

        toolchain_file_name = self.builddir / "toolchain.cmake"
        with toolchain_file_name.open("w") as toolchain_file:
            toolchain_file.write("set(CMAKE_SYSTEM_NAME Linux)\n")
            toolchain_file.write(
                "set(CMAKE_SYSTEM_PROCESSOR {})\n".format(self.cc.machine.value)
            )
            toolchain_file.write("\n")
            toolchain_file.write(
                "set(CMAKE_SYSROOT {})\n".format(self.cc.sysroot)
            )
            toolchain_file.write(
                "set(CMAKE_STAGING_PREFIX {})\n".format(
                    self.builddir / "install"
                )
            )
            toolchain_file.write("\n")
            toolchain_file.write(
                "set(CMAKE_C_COMPILER {}/{})\n".format(
                    self.cc.bin_path, self.cc.cc
                )
            )
            toolchain_file.write(
                "set(CMAKE_CXX_COMPILER {}/{})\n".format(
                    self.cc.bin_path, self.cc.cxx
                )
            )
            toolchain_file.write("\n")
            toolchain_file.write(
                "set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)\n"
            )
            toolchain_file.write(
                "set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)\n"
            )
            toolchain_file.write(
                "set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)\n"
            )
            toolchain_file.write(
                "set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)\n"
            )
            toolchain_file.write("\n")

        cache_file_name = self.builddir / "cache.cmake"
        with cache_file_name.open("w") as cache_file:
            cache_file.write("#Compiler options \n")
            cflags = self.cc.cflags
            cache_file.write(
                'set(CMAKE_C_FLAGS_DEBUG          "{} -g" CACHE STRING "")\n'.format(
                    cflags
                )
            )
            cache_file.write(
                'set(CMAKE_C_FLAGS_MINSIZEREL     "{} -DNDEBUG" CACHE STRING "")\n'.format(
                    cflags
                )
            )
            cache_file.write(
                'set(CMAKE_C_FLAGS_RELWITHDEBINFO "{} -g -DNDEBUG" CACHE STRING "")\n'.format(
                    cflags
                )
            )
            cache_file.write(
                'set(CMAKE_C_FLAGS_RELEASE        "{} -DNDEBUG" CACHE STRING "")\n'.format(
                    cflags
                )
            )
            cache_file.write("\n")

            cxxflags = self.cc.cxxflags
            cache_file.write(
                'set(CMAKE_CXX_FLAGS_DEBUG          "{} -g" CACHE STRING "")\n'.format(
                    cxxflags
                )
            )
            cache_file.write(
                'set(CMAKE_CXX_FLAGS_MINSIZEREL     "{} -DNDEBUG" CACHE STRING "")\n'.format(
                    cxxflags
                )
            )
            cache_file.write(
                'set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "{} -g -DNDEBUG" CACHE STRING "")\n'.format(
                    cxxflags
                )
            )
            cache_file.write(
                'set(CMAKE_CXX_FLAGS_RELEASE        "{} -DNDEBUG" CACHE STRING "")\n'.format(
                    cxxflags
                )
            )

        definitions = " ".join(["-D{}".format(d) for d in cmake_definitions])

        with c.cd(str(self.builddir)):
            command = "cmake -DCMAKE_BUILD_TYPE='RELWITHDEBINFO' -DCMAKE_TOOLCHAIN_FILE=toolchain.cmake -C cache.cmake {} {}".format(
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
