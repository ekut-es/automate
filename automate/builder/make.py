import logging
from pathlib import Path, PosixPath

from ruamel.yaml import YAML

from ..utils.network import rsync
from .builder import BaseBuilder


class MakefileBuilder(BaseBuilder):
    @property
    def buildvars_filename(self):
        buildvars_fname = self.builddir / "buildvars.yml"
        return buildvars_fname

    def configure(self, c):
        self._mkbuilddir()
        c.run(f"rsync -ar --delete {self.srcdir} {self.builddir}")

        buildvars = {}
        buildvars["CC"] = self.cc.bin_path / self.cc.cc
        buildvars["CXX"] = self.cc.bin_path / self.cc.cxx
        buildvars["CFLAGS"] = self.cc.cflags
        buildvars["CXXFLAGS"] = self.cc.cxxflags
        buildvars["LDFLAGS"] = self.cc.ldflags
        buildvars["LDLIBS"] = ""

        with self.buildvars_filename.open("w") as buildvars_file:
            yaml = YAML(typ="unsafe")
            yaml.dump(buildvars, buildvars_file)

    def build(self, c):
        yaml = YAML(typ="unsafe")
        with self.buildvars_filename.open("r") as buildvars_file:
            buildvars = yaml.load(buildvars_file)

        with c.cd(str(self.builddir / self.srcdir.name)):
            c.run(
                f"make CC=\"{buildvars['CC']}\" CXX=\"{buildvars['CXX']}\" CFLAGS=\"{buildvars['CFLAGS']}\" CXXFLAGS=\"{buildvars['CXXFLAGS']}\" LDFLAGS=\"{buildvars['LDFLAGS']}\" LDLIBS=\"{buildvars['LDLIBS']}\""
            )

    def install(self, c):
        """Do nothing"""
        logging.warning("Install does nothing with make builder")

    def deploy(self, c, delete=False):
        """Deploy package on board
        
           Just copies the build directory to the rundir 
        """

        with self.cc.board.connect() as con:
            rsync(
                con,
                source=str(self.builddir / self.srcdir.name) + "/",
                target=str(self.cc.board.rundir / self.srcdir.name),
                delete=delete,
                rsync_opts="-l",
            )
