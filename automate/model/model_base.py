from datetime import datetime
from pathlib import Path
from typing import Dict

from pydantic import BaseModel


class DataModelBase(BaseModel):
    class Config:
        anystr_strip_whitespace = True
        validate_all = True
        extra = "forbid"
        allow_mutation = True
        allow_population_by_field_name = True

    def _get_env_dict(self) -> Dict[str, str]:
        return {}


class LoadedModelBase(DataModelBase):
    model_file: Path
    model_file_mtime: datetime

    def _get_env_dict(self) -> Dict[str, str]:
        return {
            "model_file": str(self.model_file),
            "model_dir": str(self.model_file.parent),
        }


class DBModelBase(DataModelBase):
    id: int  # Database ID

    class Config(DataModelBase.Config):
        orm_mode = True
