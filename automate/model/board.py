from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Dict, Any

import ruamel.yaml as yaml

from .common import *


class BoardModel(BaseModel):
    pass


class LoadedBoardModel(BoardModel):
    pass
