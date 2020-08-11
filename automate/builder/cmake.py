from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Union

from ..utils.network import rsync
from .builder import BaseBuilder

if TYPE_CHECKING:
    import automate.board
    import automate.compiler


class CMakeBuilder(BaseBuilder):
    def configure(
        self,
        cross_compiler: "Optional[automate.compiler.CrossCompiler]" = None,
        srcdir: Union[Path, str] = "",
        prefix: Union[Path, str] = "",
        extra_flags: Optional[Dict[str, str]] = None,
        override_flags: Optional[Dict[str, str]] = None,
        cmake_definitions: List[str] = [],
    ):
        """
        Configure cmake based build

        # Arguments 
        cross_compiler: cross compiler for the build, default: use default compiler for the board
        srcdir: directory conaining CMakeLists.txt
        prefix: install prefix on the board
        cmake_definitions: extra cmake definitions 
        """
        super(CMakeBuilder, self).configure(
            cross_compiler=cross_compiler,
            srcdir=srcdir,
            prefix=prefix,
            extra_flags=extra_flags,
            override_flags=override_flags,
        )

        cross_compiler = self.cross_compiler

        self.clean()
        self._mkbuilddir()

        toolchain_file_name = self.builddir / "toolchain.cmake"
        with toolchain_file_name.open("w") as toolchain_file:
            toolchain_file.write("set(CMAKE_SYSTEM_NAME Linux)\n")
            toolchain_file.write(
                "set(CMAKE_SYSTEM_PROCESSOR {})\n".format(
                    cross_compiler.machine.value
                )
            )
            toolchain_file.write("\n")
            toolchain_file.write(
                "set(CMAKE_SYSROOT {})\n".format(cross_compiler.sysroot)
            )
            toolchain_file.write(
                "set(CMAKE_STAGING_PREFIX {})\n".format(
                    self.builddir / "install"
                )
            )
            toolchain_file.write("\n")
            toolchain_file.write(
                "set(CMAKE_C_COMPILER {}/{})\n".format(
                    cross_compiler.bin_path, cross_compiler.cc
                )
            )
            toolchain_file.write(
                "set(CMAKE_CXX_COMPILER {}/{})\n".format(
                    cross_compiler.bin_path, cross_compiler.cxx
                )
            )

            toolchain_file.write(
                "set(CMAKE_AR {}/{})\n".format(
                    cross_compiler.bin_path, cross_compiler.ar
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
            cflags = cross_compiler.cflags
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

            cxxflags = cross_compiler.cxxflags
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

        with self.context.cd(str(self.builddir)):
            command = "cmake -DCMAKE_BUILD_WITH_INSTALL_RPATH=ON -DCMAKE_INSTALL_RPATH={2}/lib -DCMAKE_BUILD_TYPE='RELWITHDEBINFO' -DCMAKE_TOOLCHAIN_FILE=toolchain.cmake -C cache.cmake {0} {1}".format(
                self.srcdir, definitions, self.prefix
            )
            self.logger.info("Running cmake: {}".format(command))
            self.context.run(command)

        self._save_state()

    def build(self, c):
        "Run cmake build"
        self._mkbuilddir()
        with self.context.cd(str(self.builddir)):
            self.context.run("cmake --build  .")

    def install(self, c):
        "Run cmake install"
        with self.context.cd(str(self.builddir)):
            self.context.run("cmake  --build . --target install")

    def deploy(self, c, delete=False):
        """ Deploy target on board
        
        # Arguments
        delete: if true clean install prefix before deployment
        """
        print("Rsyncing with prefix", self.prefix)
        with self.board.connect() as con:
            con.run(f"mkdir -p {self.prefix.name}")
            rsync(
                con,
                source=str(self.builddir / "install") + "/",
                target=str(self.prefix),
                delete=delete,
                rsync_opts="-l",
            )
