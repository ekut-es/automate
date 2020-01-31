import logging
from pathlib import Path, PosixPath

from ruamel.yaml import YAML

from ..utils.network import rsync
from .builder import BaseBuilder


class MakefileBuilder(BaseBuilder):
    def configure(self, cross_compiler=None, srcdir="", prefix=""):
        """ Configure a makefile build
        
            1. Copy source directory to build directory 
            2. Record build variables in build_directory/buildvars.yml
        """

        if cross_compiler is None:
            cross_compiler = self.board.compiler()

        if srcdir:
            self.state.srcdir = Path(srcdir).absolute()

        if prefix:
            self.state.prefix = Path(prefix).absolute()

        self._mkbuilddir()
        self.context.run(f"rsync -ar --delete {self.srcdir} {self.builddir}")

        buildvars = {}
        buildvars["CC"] = cross_compiler.bin_path / cross_compiler.cc
        buildvars["CXX"] = cross_compiler.bin_path / cross_compiler.cxx
        buildvars["CFLAGS"] = cross_compiler.cflags
        buildvars["CXXFLAGS"] = cross_compiler.cxxflags
        buildvars["LDFLAGS"] = cross_compiler.ldflags
        buildvars["LDLIBS"] = cross_compiler.libs

        self.state.buildvars = buildvars

        self._save_state()

    def build(self):
        """Run make with default target and set BUILDVARS for board"""

        buildvars = self.state.buildvars

        with self.context.cd(str(self.builddir / self.srcdir.name)):
            self.context.run(
                f"make CC=\"{buildvars['CC']}\" CXX=\"{buildvars['CXX']}\" CFLAGS=\"{buildvars['CFLAGS']}\" CXXFLAGS=\"{buildvars['CXXFLAGS']}\" LDFLAGS=\"{buildvars['LDFLAGS']}\" LDLIBS=\"{buildvars['LDLIBS']}\""
            )

    def install(self):
        """Do nothing"""
        logging.warning("Install does nothing with make builder")

    def deploy(self, delete=False):
        """Deploy package on board
        
           Just copies build_directory/srcdir_name to the rundir

           # Arguments 

           delete: if true delete non existant files from the board
        """

        with self.board.connect() as con:
            with con.cd(str(self.board.rundir)):
                con.run(f"mkdir -p {self.srcdir.name}")
            rsync(
                con,
                source=str(self.builddir / self.srcdir.name) + "/",
                target=str(self.board.rundir / self.srcdir.name),
                delete=delete,
                rsync_opts="-l",
            )
