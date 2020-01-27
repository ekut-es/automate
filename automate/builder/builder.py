import logging
import os
import shutil
from pathlib import Path
from string import Template
from typing import Union

from .. import compiler
from ..utils import untar
from ..utils.kernel import KernelConfigBuilder, KernelData
from ..utils.network import rsync
from ..utils.uboot import build_ubimage


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
            self.prefix = Path(cc.board.rundir) / self.srcdir.name

        self.prefix = self.prefix.absolute()
        self.srcdir = self.srcdir.absolute()
        self.builddir = self.builddir.absolute()

        self.logger = logging.getLogger(__name__)

    @property
    def board(self):
        return self.cc.board

    def configure(self, c):
        "Configure the build"

        raise NotImplementedError("Configure is not implemented")

    def build(self, c):
        "Build target code"
        raise NotImplementedError("Build is not implemented")

    def install(self, c):
        "Installs the build in local directory"
        raise NotImplementedError("Installation is not implemented")

    def deploy(self, c):
        "Deploys installed binary to the board"
        raise NotImplementedError("Installation is not implemented")

    def clean(self, c):
        "Removes the builddir"
        if self.builddir != self.srcdir:
            if self.builddir.exists():
                shutil.rmtree(self.builddir)

    def _mkbuilddir(self):
        "Creates the build directory"
        self.builddir.mkdir(parents=True, exist_ok=True)


class SPECBuilder(BaseBuilder):
    # TODO: implement spec Builder
    pass


class AutotoolsBuilder(BaseBuilder):
    # TODO: implement autotools Builder
    pass
