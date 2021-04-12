from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel

from .board import BoardModel
from .compiler import CompilerModel
from .model_base import *


class MetadataModel(DataModelBase):
    compilers: List[CompilerModel]
    boards: List[BoardModel]
