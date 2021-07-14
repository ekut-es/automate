from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from .common import *
from .model_base import *


class TripleModel(DataModelBase):
    """Description of a target triple"""

    machine: Machine
    vendor: str = ""
    os: OS
    environment: Environment


class CompilerModel(LoadedModelBase):
    name: str
    triples: List[TripleModel] = Field(
        ..., description="List of supported target triples"
    )
    toolchain: Toolchain
    version: VersionString
    basedir: str
    runtime: str = ""
    cc: str
    cxx: str
    asm: str
    ld: str
    ar: str
    isa_map: Dict[str, str]
    uarch_map: Dict[str, str]
    feature_map: Dict[str, str] = Field(default_factory=dict)
    description: str = ""
    prefix: str = ""
    postfix: str = ""
    multiarch: bool = Field(
        False,
        description="Flag to indicate that this compiler supports builds with multiarch sysroots",
    )
