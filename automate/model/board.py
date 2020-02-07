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

class PowerConnectorModel(DataModelBase):
    name: str

class BoardModel(DataModelBase):
    name: str
    hostname: str = ""      # FIXME use pydantic datatypes
    mac_address : str = ""  # FIXME use pydantic datatypes
    board: str
    description: str
    rundir: Path
    doc: List[DocumentationLinkModel] = []
    gateway: Optional[GatewayModel] = None
    connections: List[Union[SSHConnectionModel, UARTConnectionModel]]
    cores: List[CoreModel]
    os: OSModel
    
    soc: Optional[SOCModel] = None 
    power_connector: Optional[PowerConnectorModel] = None
    #TODO: maybe move to power connector
    voltage : Optional[float] = None      #  voltage in V
    max_current : Optional[float] = None  # max. current in A
    
    
    

    def _get_env_dict(self) -> Dict[str, str]:
        default_dict = dict(super(BoardModel, self)._get_env_dict())

        d = {"board": self.board, "board_name": self.name}

        default_dict.update(d)

        return default_dict

class BoardModelFS(BoardModel, LoadedModelBase):
    """Adds fields like file_name and file_modification time 
    that are only meaningful for models loaded from Filesystem""" 
    pass
