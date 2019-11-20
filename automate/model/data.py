from pydantic import BaseModel, Schema
from enum import Enum
from typing import List, Dict, Any

from .compiler import LoadedCompilerModel
from .board import LoadedBoardModel


class DataModel(BaseModel):
    compilers: List[LoadedCompilerModel]
    boards: List[LoadedBoardModel]
