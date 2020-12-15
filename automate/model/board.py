from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, HttpUrl

from .common import *
from .compiler import TripleModel
from .model_base import *


class DocumentationLinkModel(DataModelBase):
    title: str
    location: Union[HttpUrl, Path] = Field(..., alias="loc")


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
    num: int = Field(..., alias="os_id")
    isa: str
    uarch: str
    vendor: str = Field(..., alias="implementer")
    extensions: List[str] = []
    description: str = ""


class UBootModel(DataModelBase):
    loadaddr: str
    image_name: Path
    image_compression: str = "none"
    dtb_image: Path
    dtb_compression: str = "none"


class KernelImageModel(DataModelBase):
    build_path: Path
    deploy_path: Path


class KernelModel(DataModelBase):
    name: str
    description: str
    version: VersionString
    commandline: str
    kernel_config: Path = Field(..., alias="config")
    kernel_source: Path = Field(..., alias="source")
    kernel_srcdir: Path = Field(..., alias="srcdir")
    image: KernelImageModel
    uboot: Optional[UBootModel] = None
    default: bool = False


class OSModel(DataModelBase):
    triple: TripleModel
    distribution: str
    release: str
    description: str
    sysroot: Path = Path("$(boardroot)/$(board_name)/sysroot")
    rootfs: Path = Path("$(boardroot)/$(board_name)/$(board_id).img")
    multiarch: bool = False
    kernels: List[KernelModel] = []


class FoundryModel(DataModelBase):
    name: str


class SOCModel(DataModelBase):
    name: str
    technology: int
    foundry: FoundryModel


class PowerSupplyModel(DataModelBase):
    name: str
    voltage: float  #  voltage in V
    max_current: float  # max. current in A


class BoardModel(DataModelBase):
    name: str
    board: str
    hostname: str = ""  # FIXME use pydantic datatypes
    mac_address: str = ""  # FIXME use pydantic datatypes
    description: str
    rundir: Path
    doc: List[DocumentationLinkModel] = []
    gateway: Optional[GatewayModel] = None
    connections: List[Union[SSHConnectionModel, UARTConnectionModel]]
    cores: List[CoreModel]
    os: OSModel

    soc: Optional[SOCModel] = None
    power_supply: Optional[PowerSupplyModel] = None
    reset: List[str] = []

    def _get_env_dict(self) -> Dict[str, str]:
        default_dict = dict(super(BoardModel, self)._get_env_dict())

        d = {"board": self.board, "board_name": self.name}

        default_dict.update(d)

        return default_dict


class BoardModelFS(BoardModel, LoadedModelBase):
    """Adds fields like file_name and file_modification time 
    that are only meaningful for models loaded from Filesystem"""

    pass


class BoardModelDB(BoardModel, DBModelBase):
    """Add data model field id:int for database id"""

    pass
