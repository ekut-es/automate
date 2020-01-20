import logging
import os
import string
from datetime import datetime
from glob import glob
from pathlib import Path
from typing import Any, Dict, List, Optional

import ruamel.yaml as yaml
from ruamel.yaml.comments import CommentedMap

from .config import AutomateConfig
from .model import DataModelBase, LoadedModelBase, MetadataModel, UsersModel


class ModelLoader(object):
    def __init__(self, config: AutomateConfig) -> None:
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.logger.debug(
            "Metadata Loader for {}".format(self.config.automate.metadata)
        )

        self.model = None

    def _load_metadata_list(
        self, pattern: str, recursive: bool = True
    ) -> List[CommentedMap]:
        res = []
        glob_pattern = os.path.join(self.config.automate.metadata, pattern)
        self.logger.debug("Load glob pattern: {}".format(str(glob_pattern)))
        files = glob(glob_pattern, recursive=recursive)

        for file_name in files:
            self.logger.debug("Loading metadata from {}".format(file_name))
            with open(file_name) as f:
                mtime = datetime.utcfromtimestamp(os.path.getmtime(file_name))
                yaml_dict = yaml.load(f, yaml.RoundTripLoader)
                yaml_dict["model_file"] = file_name
                yaml_dict["model_file_mtime"] = mtime
                res.append(yaml_dict)

        return res

    def _apply_templates(
        self, data_model: DataModelBase, env: Dict[str, str]
    ) -> None:

        env = dict(env)
        env.update(data_model._get_env_dict())

        def do_apply_template(template, env):
            try:
                self.logger.debug("Template is: {}".format(template.template))
                formatted = template.substitute(env)
                self.logger.debug("Formatted field: {}".format(formatted))
                return formatted
            except ValueError as e:  # pragma: no cover
                self.logger.error(str(e))
                self.logger.error(
                    "During formatting of field {} from {}".format(
                        field_name, field
                    )
                )
                self.logger.error(str(env))
                raise e

        for field_name in data_model.__fields__:
            self.logger.debug("Field_name is: {}".format(field_name))
            field = getattr(data_model, field_name)
            self.logger.debug("Field is: {}".format(field))

            formatted = ""
            if isinstance(field, str):
                template = string.Template(field)
                formatted = do_apply_template(template, env)
                setattr(data_model, field_name, formatted)
            elif isinstance(field, Path):

                template = string.Template(str(field))
                formatted = do_apply_template(template, env)

                formatted_path = Path(formatted)

                setattr(data_model, field_name, formatted_path)

            elif isinstance(field, DataModelBase):
                self._apply_templates(field, env)
            elif isinstance(field, list):
                for item in field:
                    if isinstance(item, DataModelBase):
                        self._apply_templates(item, env)

        return None

    def load(self) -> MetadataModel:
        compilers = self._load_metadata_list("compilers/**/description.yml")
        boards = self._load_metadata_list("boards/**/description.yml")

        data_model = MetadataModel(compilers=compilers, boards=boards)

        template_env = {
            "metadata": os.path.expanduser(str(self.config.automate.metadata)),
            "toolroot": os.path.expanduser(str(self.config.automate.toolroot)),
            "boardroot": os.path.expanduser(
                str(self.config.automate.boardroot)
            ),
        }

        self.logger.debug("Applying templates")
        self._apply_templates(data_model, template_env)

        self.logger.debug("Datadict after applying templates")
        self.logger.debug(data_model.dict())

        return data_model

    def load_users(self) -> UsersModel:
        metadata_path = Path(
            os.path.expanduser(str(self.config.automate.metadata))
        )
        users_file = metadata_path / "users.yml"

        with users_file.open() as f:
            mtime = datetime.utcfromtimestamp(os.path.getmtime(users_file))
            yaml_dict = yaml.load(f, yaml.RoundTripLoader)

            users_model = UsersModel(
                users=dict(yaml_dict),
                model_file=str(users_file),
                model_file_mtime=mtime,
            )

        return users_model
