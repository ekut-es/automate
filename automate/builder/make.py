import logging
from pathlib import Path, PosixPath
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from ruamel.yaml import YAML

from ..utils.network import rsync
from .builder import BaseBuilder

if TYPE_CHECKING:
    import automate.compiler


class MakefileBuilder(BaseBuilder):
    def configure(
        self,
        cross_compiler: "Optional[automate.compiler.CrossCompiler]" = None,
        srcdir: Union[Path, str] = "",
        prefix: Union[Path, str] = "",
        extra_flags: Optional[Dict[str, str]] = None,
        override_flags: Optional[Dict[str, str]] = None,
    ):
        """ Configure a makefile build

            1. Copy source directory to build directory
            2. Record build variables in build_directory/buildvars.yml
        """

        super(MakefileBuilder, self).configure(
            cross_compiler=cross_compiler,
            srcdir=srcdir,
            prefix=prefix,
            extra_flags=extra_flags,
            override_flags=override_flags,
        )

        cross_compiler = self.cross_compiler

        self._mkbuilddir()

        if Path.is_file(Path(f"{self.srcdir}/.automateignore")):
            self.context.run(f"rsync -ar --exclude \'.automateignore\' --exclude-from={self.srcdir}/.automateignore --delete {self.srcdir} {self.builddir}")
        else:
            self.context.run(f"rsync -ar --exclude \'.automateignore\' --delete {self.srcdir} {self.builddir}")

        buildvars: Dict[str, Any] = {}
        buildvars["CC"] = cross_compiler.bin_path / cross_compiler.cc
        buildvars["CXX"] = cross_compiler.bin_path / cross_compiler.cxx
        buildvars["AR"] = cross_compiler.bin_path / cross_compiler.ar
        buildvars["CFLAGS"] = cross_compiler.cflags
        buildvars["CXXFLAGS"] = cross_compiler.cxxflags
        buildvars["LDFLAGS"] = cross_compiler.ldflags
        buildvars["LDLIBS"] = cross_compiler.libs

        self.state.buildvars = buildvars

        self._save_state()

    def build(self, target=""):
        """Run make with default target and set BUILDVARS for board"""

        buildvars = self.state.buildvars

        with self.context.cd(str(self.builddir / self.srcdir.name)):
            self.context.run(
                f"make -j{self._num_build_cpus()} {target} CC=\"{buildvars['CC']}\" CXX=\"{buildvars['CXX']}\" AR=\"{buildvars['AR']}\" CFLAGS=\"{buildvars['CFLAGS']}\" CXXFLAGS=\"{buildvars['CXXFLAGS']}\" LDFLAGS=\"{buildvars['LDFLAGS']}\" LDLIBS=\"{buildvars['LDLIBS']}\""
            )

    def install(self):
        """Do nothing"""
        logging.warning("Install does nothing with make builder")

    def deploy(self, connection=None, delete=False):
        """Deploy package on board

           Just copies build_directory/srcdir_name to the rundir

           # Arguments

           delete: if true delete remove non existant files from install prefix on the board
        """
        if connection == None:
            with self.board.connect() as con:
                self.deploy_internal(con, delete)
        else:
            self.deploy_internal(connection, delete)

    def deploy_internal(self, con, delete=False):
        """Deploy package on board (see deploy())

           # Arguments

           con: Connection object

           delete: see deploy()
        """
        with con.cd(str(self.board.rundir)):
            con.run(f"mkdir -p {self.srcdir.name}")
        rsync(
            con,
            source=str(self.builddir / self.srcdir.name) + "/",
            target=str(self.board.rundir / self.srcdir.name),
            delete=delete,
            rsync_opts="-l",
        )

