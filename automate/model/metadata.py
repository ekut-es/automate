from pydantic import BaseModel, Schema
from enum import Enum
from typing import List, Dict, Any


from .compiler import CompilerModel
from .board import BoardModel
from .model_base import *


class MetadataModel(DataModelBase):
    compilers: List[CompilerModel]
    boards: List[BoardModel]
