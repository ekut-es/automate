import io
import logging
import os
import string
from datetime import datetime
from glob import glob
from pathlib import Path
from typing import Any, Dict, List, Optional

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

from .config import AutomateConfig
from .model import (
    BoardModel,
    BoardModelFS,
    CompilerModel,
    DataModelBase,
    LoadedModelBase,
    MetadataModel,
    UsersModel,
    VersionString,
)


class ModelLoader(object):
    def __init__(self, config: AutomateConfig, database=None) -> None:
        """Initialize model loader

        # Parameters
        config: AutomateConfig object to use for search of metadata locations
        database: optional database connnection
        """

        self.config = config
        self.database = database

        self.logger = logging.getLogger(__name__)
        self.logger.debug(
            "Metadata Loader for {}".format(self.config.automate.metadata)
        )
        self.yaml = YAML()

        self.model = None

    def _load_metadata_list(
        self, pattern: str, recursive: bool = True
    ) -> List[CommentedMap]:
        """Parse yaml files for metadata information

        # Arguments
        pattern: glob_pattern to search for metadata files
        recursive: wether search allows ** in glob patterns to recurse into subdirectories
        """
        res = []
        glob_pattern = os.path.join(
            os.path.expanduser(self.config.automate.metadata), pattern
        )
        self.logger.debug("Load glob pattern: {}".format(str(glob_pattern)))
        files = glob(glob_pattern, recursive=recursive)

        for file_name in files:
            self.logger.debug("Loading metadata from {}".format(file_name))
            with io.open(file_name, encoding="utf-8") as f:
                mtime = datetime.utcfromtimestamp(os.path.getmtime(file_name))

                yaml_dict = self.yaml.load(f)
                yaml_dict["model_file"] = file_name
                yaml_dict["model_file_mtime"] = mtime
                res.append(yaml_dict)

        return res

    def _merge_metadata(self, *args):
        """ Merge multiple lists of Models """
        merged_list = []
        merged_names = set()
        for arg in args:
            for item in arg:
                if item.name in merged_names:
                    continue
                merged_list.append(item)
                merged_names.add(item.name)

        merged_list.sort(key=lambda x: x.name)
        return merged_list

    def _apply_templates(
        self, data_model: DataModelBase, env: Dict[str, str]
    ) -> None:
        """ Expand template parameters from env in strings from data_model """

        env = dict(env)
        env.update(data_model._get_env_dict())

        def do_apply_template(template, env):
            try:
                formatted = template.safe_substitute(env)
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
            field = getattr(data_model, field_name)

            formatted = ""
            if isinstance(field, str) and not isinstance(field, VersionString):
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

    def load(self, expand_templates=True) -> MetadataModel:
        """Load Metadata model

        # Arguments:
            expand_templates: boolean if true ${var} templates Paths are replaced by their respective configuration value

        # Templates
        Expand templates currently expands the following templates
        ${metadata}: metadata location from config
        ${toolroot}: toolroot from config  used to give relative paths for compilers
        ${boardroot}: boardroot from config used to store kernel_sources, rootfs_images, board sysroots, cached_builds
        """
        compiler_map = self._load_metadata_list("compilers/**/description.yml")
        compilers = [CompilerModel(**c) for c in compiler_map]

        board_dicts = self._load_metadata_list("boards/**/description.yml")
        boards = []
        for board_dict in board_dicts:
            try:
                board = BoardModelFS(**board_dict)
                boards.append(board)
            except Exception as e:
                self.logger.error(
                    "Could not validate board description from: %s",
                    str(board_dict["model_file"]),
                )
                self.logger.error(str(e))

        if self.database:
            self.logger.info("getting boards from database")
            database_boards = self.database.get_all_boards()
            self.logger.info(
                "Boards from database %s",
                " ".join((b.name for b in database_boards)),
            )
            boards = self._merge_metadata(boards, database_boards)

        data_model = MetadataModel(compilers=compilers, boards=boards)

        if expand_templates:
            self.logger.info("Expanding templates in metadata files")
            template_env = {
                "metadata": os.path.expanduser(
                    str(self.config.automate.metadata)
                ),
                "toolroot": os.path.expanduser(
                    str(self.config.automate.toolroot)
                ),
                "boardroot": os.path.expanduser(
                    str(self.config.automate.boardroot)
                ),
            }

            self._apply_templates(data_model, template_env)

        return data_model

    def load_users(self) -> UsersModel:
        """ Load user data """
        metadata_path = Path(
            os.path.expanduser(str(self.config.automate.metadata))
        )
        users_file = metadata_path / "users.yml"

        with io.open(users_file, encoding="utf-8") as f:
            mtime = datetime.utcfromtimestamp(os.path.getmtime(users_file))
            yaml_dict = self.yaml.load(f)

            users_model = UsersModel(
                users=dict(yaml_dict),
                model_file=str(users_file),
                model_file_mtime=mtime,
            )

        return users_model
