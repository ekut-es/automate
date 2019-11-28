from pydantic import BaseModel
from datetime import datetime
from pathlib import Path

from typing import Dict


class DataModelBase(BaseModel):
    class Config:
        anystr_strip_whitespace = True
        validate_all = True
        extra = "forbid"
        allow_mutation = True

    def _get_env_dict(self) -> Dict[str, str]:
        return {}


class LoadedModelBase(DataModelBase):
    model_file: Path
    model_file_mtime: datetime
