from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Dict, Any

import ruamel.yaml as yaml

from .common import *
from .model_base import *


class TripleModel(DataModelBase):
    """Description of a target triple"""
    machine: Machine
    vendor: Vendor = Vendor.UNKNOWN
    os: OS
    environment: Environment


class CompilerModel(LoadedModelBase):
    name: str
    id: str
    triples: List[TripleModel] = Field(...,
                                       description="List of supported target triples")
    toolchain: Toolchain
    version: str
    basedir: str
    cc: str
    cxx: str
    asm: str
    ld: str
    isa_map: Dict[ISA, str]
    uarch_map: Dict[UArch, str]
    description: str = ""
    prefix: str = ""
    postfix: str = ""
    multiarch: bool = Field(False,
                            description="Flag to indicate that this compiler supports builds with multiarch sysroots")
