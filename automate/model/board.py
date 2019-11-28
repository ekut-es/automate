from pydantic import BaseModel, Field, HttpUrl
from enum import Enum
from typing import List, Dict, Any, Union, Optional
from pathlib import Path

import ruamel.yaml as yaml

from .common import *
from .model_base import *
from .compiler import TripleModel


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
    rundir: str


class UARTConnectionModel(DataModelBase):
    device: Path
    baudrate: int = 11520


class CoreModel(DataModelBase):
    id: int
    isa: ISA
    uarch: UArch


class KernelModel(DataModelBase):
    id: str
    description: str
    version: str
    localversion: Optional[str] = None
    commandline: str
    commandline_extra: Optional[str] = None
    kernel_config: Path
    kernel_source: Path
    default: bool
    isolated_cores: List[int] = []
    nohz: bool


class OSModel(DataModelBase):
    triple: TripleModel
    distribution: str
    release: str
    description: str
    sysroot: Path = Path("$(boardroot)/$(board_id)/sysroot")
    rootfs: Path = Path("$(boardroot)/$(board_id)/$(board_id).img.bz")
    multiarch: bool = False
    kernels: List[KernelModel] = []


class BoardModel(LoadedModelBase):
    name: str
    id: str
    board: str
    description: str
    doc: List[DocumentationLinkModel] = []
    gateway: Optional[GatewayModel] = None
    connections: List[Union[SSHConnectionModel, UARTConnectionModel]]
    cores: List[CoreModel]
    os: OSModel

    def _get_env_dict(self):
        d = {
            'board': self.board,
            'board_id': self.id
        }

        return d
