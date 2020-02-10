import logging
import multiprocessing
import os
import shutil
from pathlib import Path
from string import Template
from typing import TYPE_CHECKING, Dict, Optional, Union

from ruamel.yaml import YAML

from ..utils import untar
from ..utils.kernel import KernelConfigBuilder, KernelData
from ..utils.network import rsync
from ..utils.uboot import build_ubimage

if TYPE_CHECKING:
    import automate.board
    import automate.context


class BuilderState:
    builddir: Path  # Build Directory
    srcdir: Path  # Source Direcotry
    prefix: Path  # Install Prefix
    kernel: Optional[Dict[str, str]] = None
    buildvars: Optional[Dict[str, str]] = None


class BaseBuilder(object):
    def __init__(
        self,
        context: "automate.context.AutomateContext",
        board: "automate.board.Board",
        builddir: Union[Path, str] = "",
    ):
        self.logger = logging.getLogger(__name__)
        self.board = board
        self.context = context

        if builddir:
            builddir = Path(builddir)
        else:
            builddir = Path("builds") / board.id

        assert isinstance(builddir, Path)
        if not self._load_state(builddir):
            self.state = BuilderState()
            self.state.builddir = builddir
            self.state.srcdir = Path(".")
            self.state.prefix = Path(self.board.rundir) / self.srcdir.name

            self.state.srcdir = self.state.srcdir.absolute()
            self.state.builddir = self.state.builddir.absolute()

    @property
    def builddir(self) -> Path:
        return self.state.builddir

    @property
    def srcdir(self) -> Path:
        return self.state.srcdir

    @property
    def prefix(self) -> Path:
        return self.state.prefix

    def _num_build_cpus(self) -> int:
        """ Return number of local cpus for build"""
        return multiprocessing.cpu_count()

    def _save_state(self) -> None:
        self._mkbuilddir()
        yaml = YAML(typ="unsafe")
        state_file = self.builddir / ".builder_state.yml"
        with state_file.open("w") as state_file_obj:
            yaml.dump(self.state, state_file_obj)

    def _load_state(self, builddir: Path) -> bool:
        state_file = builddir / ".builder_state.yml"
        if state_file.exists():
            yaml = YAML(typ="unsafe")
            with state_file.open() as state_file_obj:
                self.state = yaml.load(state_file_obj)

            return True

        return False

    def configure(self, *args, **kwargs):
        "Configure the build"

        raise NotImplementedError("Configure is not implemented")

    def build(self, *args, **kwargs):
        "Build target code"
        raise NotImplementedError("Build is not implemented")

    def install(self, *args, **kwargs):
        "Installs the build in local directory"
        raise NotImplementedError("Installation is not implemented")

    def deploy(self, *args, **kwargs):
        "Deploys installed binary to the board"
        raise NotImplementedError("Installation is not implemented")

    def clean(self, *args, **kwargs):
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
