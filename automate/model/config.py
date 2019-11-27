from .model_base import *
from pathlib import Path


class ConfigModel(DataModelBase):
    metadata: Path
    identity: Path
    toolroot: Path
    boardroot: Path
