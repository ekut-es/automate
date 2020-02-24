from typing import Dict, List, Optional

from .model_base import DataModelBase, LoadedModelBase


class UserModel(DataModelBase):
    name: str
    mail: str
    public_keys: List[str]


class UsersModel(LoadedModelBase):
    users: Dict[str, UserModel]
