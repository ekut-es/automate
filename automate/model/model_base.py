from pydantic import BaseModel
from datetime import datetime


class DataModelBase(BaseModel):
    class Config:
        anystr_strip_whitespace = True
        validate_all = True
        extra = "forbid"
        allow_mutation = False


class LoadedModelBase(DataModelBase):
    model_file: str
    model_file_mtime: datetime
