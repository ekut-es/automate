import logging
from glob import glob
import os
import string
from datetime import datetime
import ruamel.yaml as yaml

from .model import DataModel, DataModelBase, LoadedModelBase

from .config import configure

from typing import List, Dict, Any, Optional
from pathlib import Path


from ruamel.yaml.comments import CommentedMap


class ModelLoader(object):
    def __init__(self) -> None:
        self.config = configure()
        self.logger = logging.getLogger(__name__)
        self.logger.debug(
            "Metadata Loader for {}".format(self.config.metadata))

        self.model = None

    def _load_metadata_list(self, pattern: str, recursive: bool = True) -> List[CommentedMap]:
        res = []
        files = glob(os.path.join(self.config.metadata,
                                  pattern), recursive=recursive)

        for file_name in files:
            self.logger.debug("Loading metadata from {}".format(file_name))
            with open(file_name) as f:
                mtime = datetime.utcfromtimestamp(os.path.getmtime(file_name))
                yaml_dict = yaml.load(f, yaml.RoundTripLoader)
                yaml_dict["model_file"] = file_name
                yaml_dict["model_file_mtime"] = mtime
                res.append(yaml_dict)

        return res

    def _apply_templates(self,
                         data_model: DataModelBase,
                         env: Dict[str, str],
                         model_file: Optional[Path] = None) -> None:

        env = dict(env)
        env.update(data_model._get_env_dict())

        if isinstance(data_model, LoadedModelBase):
            model_file = data_model.model_file

        def do_apply_template(template, env):
            try:
                logging.debug("Template is: {}".format(template.template))
                formatted = template.substitute(env)
                logging.debug("Formatted field: {}".format(formatted))
                return formatted
            except ValueError as e:
                logging.error(str(e))
                logging.error("During formatting of field {} from {} value: {}".format(
                    field_name, model_file, field))
                logging.error(str(env))
                raise e

        for field_name in data_model.__fields__:
            logging.debug("Field_name is: {}".format(field_name))
            field = getattr(data_model, field_name)
            logging.debug("Field is: {}".format(field))

            formatted = ""
            if isinstance(field, str):
                template = string.Template(field)
                formatted = do_apply_template(template, env)
                setattr(data_model, field_name, formatted)
            elif isinstance(field, Path):

                template = string.Template(str(field))
                formatted = do_apply_template(template, env)

                formatted_path = Path(formatted)

                if not formatted_path.is_absolute():
                    if model_file is not None:
                        formatted_path = model_file.parent / formatted_path
                setattr(data_model, field_name, formatted)

            elif isinstance(field, DataModelBase):
                self._apply_templates(field,
                                      env,
                                      model_file)
            elif isinstance(field, list):
                for item in field:
                    if isinstance(item, DataModelBase):
                        self._apply_templates(item,
                                              env,
                                              model_file)

        return None

    def load_model(self) -> DataModel:
        compiler = self._load_metadata_list("compiler/**/description.yml")
        boards = self._load_metadata_list("boards/**/description.yml")

        data_model = DataModel(compiler=compiler, boards=boards)

        template_env = {
            'metadata':  str(self.config.metadata),
            'toolroot':  str(self.config.toolroot),
            'boardroot': str(self.config.boardroot)
        }

        self.logger.debug("Applying templates")
        self._apply_templates(data_model, template_env)

        self.logger.debug("Datadict after applying templates")
        self.logger.debug(data_model.dict())

        return data_model


_model: Optional[DataModel] = None


def get_model() -> DataModel:
    global _model
    if _model is None:
        loader = ModelLoader()
        model = loader.load_model()
        _model = model

    return _model
