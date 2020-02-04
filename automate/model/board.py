from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

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
    num: int
    isa: str
    uarch: str
    vendor: str
    extensions: List[str] = []  # Supported ISA extensions
    description: str = ""


class UBootModel(DataModelBase):
    loadaddr: str
    image_name: Path
    dtb_image: Path


class KernelImageModel(DataModelBase):
    build_path: Path
    deploy_path: Path


class KernelModel(DataModelBase):
    name: str
    description: str
    version: str
    localversion: Optional[str] = None
    commandline: str
    kernel_config: Path
    kernel_source: Path
    kernel_srcdir: Path
    image: KernelImageModel
    uboot: Optional[UBootModel] = None
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


class BoardModel(DataModelBase):
    name: str
    board: str
    description: str
    rundir: Path
    doc: List[DocumentationLinkModel] = []
    gateway: Optional[GatewayModel] = None
    connections: List[Union[SSHConnectionModel, UARTConnectionModel]]
    cores: List[CoreModel]
    os: OSModel

    def _get_env_dict(self) -> Dict[str, str]:
        default_dict = dict(super(BoardModel, self)._get_env_dict())

        d = {"board": self.board, "board_name": self.name}

        default_dict.update(d)

        return default_dict

class BoardModelFS(BoardModel, LoadedModelBase):
    """Adds fields like file_name and file_modification time 
    that are only meaningful for models loaded from Filesystem""" 
    pass
