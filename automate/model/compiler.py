from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Dict, Any

import ruamel.yaml as yaml

from .common import *


class TripleModel(BaseModel):
    """Description of a target triple"""
    machine: Machine   # type: ignore
    vendor: Vendor = Vendor.UNKNOWN  # type : ignore
    os: OS   # type: ignore
    environment: Environment  # type: ignore


class CompilerModel(BaseModel):
    name: str  # type: ignore
    id: str  # type: ignore
    # type: ignore
    triples: List[TripleModel] = Field(...,
                                       description="List of supported target triples")
    toolchain: Toolchain  # type: ignore
    version: str  # type: ignore
    basedir: str  # type: ignore
    cc: str  # type: ignore
    cxx: str  # type: ignore
    asm: str  # type: ignore
    ld: str  # type: ignore
    isa_map: Dict[ISA, str]  # type: ignore
    uarch_map: Dict[UArch, str]  # type: ignore
    description: str = ""  # type: ignore
    prefix: str = ""  # type: ignore
    postfix: str = ""  # type: ignore
    multiarch: bool = Field(
        False, description="Flag to indicate that this compiler supports builds with multiarch sysroots")  # type: ignore


class LoadedCompilerModel(CompilerModel):
    model_file: str  # type: ignore
    gcc_toolchains: List[CompilerModel] = []  # type: ignore
