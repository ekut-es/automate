from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import ruamel.yaml as yaml
from pydantic import BaseModel, Field, HttpUrl

from .common import *
from .compiler import TripleModel
from .model_base import *


class DocumentationLinkModel(DataModelBase):
    title: str
    loc: Union[HttpUrl, Path]


class GatewayModel(DataModelBase):
    host: str
    username: str
    port: int = 22


class SSHConnectionModel(DataModelBase):
    host: str
    username: str
    port: int = 22


class UARTConnectionModel(DataModelBase):
    device: Path
    baudrate: int = 11520


class CoreModel(DataModelBase):
    id: int
    isa: ISA
    uarch: UArch
    vendor: Vendor
    extensions: List[ISAExtension] = []  # Supported ISA extensions
    description: str = ""


class KernelModel(DataModelBase):
    id: str
    description: str
    version: str
    localversion: Optional[str] = None
    commandline: str
    kernel_config: Path
    kernel_source: Path
    kernel_srcdir: str = ""
    default: bool


class OSModel(DataModelBase):
    triple: TripleModel
    distribution: str
    release: str
    description: str
    sysroot: Path = Path("$(boardroot)/$(board_id)/sysroot")
    rootfs: Path = Path("$(boardroot)/$(board_id)/$(board_id).img")
    multiarch: bool = False
    kernels: List[KernelModel] = []


class BoardModel(LoadedModelBase):
    name: str
    id: str
    board: str
    description: str
    rundir: Path
    doc: List[DocumentationLinkModel] = []
    gateway: Optional[GatewayModel] = None
    connections: List[Union[SSHConnectionModel, UARTConnectionModel]]
    cores: List[CoreModel]
    os: OSModel

    def _get_env_dict(self) -> Dict[str, str]:
        d = {"board": self.board, "board_id": self.id}

        return d
