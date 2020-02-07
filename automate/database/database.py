import inspect
import logging
import os
import pprint
import sys
from datetime import datetime
from os.path import dirname, join
from typing import Any, List

from ..model import (
    BoardModel,
    BoardModelDB,
    CoreModel,
    DocumentationLinkModel,
    KernelImageModel,
    KernelModel,
    OSModel,
    SSHConnectionModel,
    TripleModel,
    UBootModel,
)

try:
    import psycopg2  # type: ignore
    import psycopg2.extras  # type: ignore
    from dotenv import load_dotenv  # type: ignore
    from jinjasql import JinjaSql  # type; ignore

    enabled = True
except:
    enabled = False


def database_enabled() -> bool:
    return enabled


class Database:
    def __init__(
        self, host: str, port: int, db: str, user: str, password: str
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.connection_string = "host={} port={} dbname={} user={} password={}".format(
            host, port, db, user, password
        )

        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password

        try:
            connection = psycopg2.connect(self.connection_string)
            self.cursor = connection.cursor(
                cursor_factory=psycopg2.extras.DictCursor
            )
        except Exception as e:
            self.logger.error(
                "could not connnect to database: '"
                + self.connection_string
                + "'"
            )
            self.logger.error(e)

        self.j = JinjaSql(param_style="pyformat")

        self.QUERIES_DIR = join(dirname(__file__), "queries")

        self.all_boards_query = self.__load_query("select_all_boards")
        self.all_cpu_cores_for_board_query = self.__load_query(
            "select_all_cpu_cores_for_board"
        )
        self.os_for_board_query = self.__load_query("select_os_for_board")
        self.all_kernels_for_os_query = self.__load_query(
            "select_all_kernels_for_os"
        )
        self.all_docs_for_board_query = self.__load_query(
            "select_all_docs_for_board"
        )
        self.insert_board_query = self.__load_query("insert_board")
        self.init_database_query = self.__load_query("init_database")

    def __load_query(self, name: str) -> str:
        sql_file_path = self.QUERIES_DIR + "/" + name + ".sql"
        try:
            sql_file = open(sql_file_path, "r")
        except:
            self.logger.error(
                "could not load sql file: '" + sql_file_path + "'"
            )
        query = sql_file.read()
        return query

    def init(self) -> None:
        query = self.init_database_query

        self.cursor.execute(query)

    def get_all_boards(self) -> List[BoardModelDB]:
        self.cursor.execute(self.all_boards_query)
        boards = self.cursor.fetchall()

        board_models = []

        for board in boards:
            query, bind_params = self.j.prepare_query(
                self.all_cpu_cores_for_board_query, {"board_id": board["id"]}
            )
            self.cursor.execute(query)
            cpu_cores = self.cursor.fetchall()

            query, bind_params = self.j.prepare_query(
                self.os_for_board_query, {"board_id": board["id"]}
            )
            self.cursor.execute(query)
            os = self.cursor.fetchone()

            query, bind_params = self.j.prepare_query(
                self.all_docs_for_board_query, {"board_id": board["id"]}
            )
            self.cursor.execute(query)
            docs = self.cursor.fetchall()

            query, bind_params = self.j.prepare_query(
                self.all_kernels_for_os_query, {"board_id": board["id"]}
            )
            self.cursor.execute(query)
            kernels = self.cursor.fetchall()

            kernel_models = []

            for kernel in kernels:
                kernel_image_model = KernelImageModel(
                    **{
                        "build_path": kernel["image_build_path"],
                        "deploy_path": kernel["image_deploy_path"],
                    }
                )

                uboot_model = None

                if (
                    kernel["uboot_loadaddr"] is not None
                    and kernel["uboot_image_name"] is not None
                    and kernel["uboot_dtb_image"] is not None
                ):
                    uboot_model = UBootModel(
                        **{
                            "loadaddr": kernel["uboot_loadaddr"],
                            "image_name": kernel["uboot_image_name"],
                            "dtb_image": kernel["uboot_dtb_image"],
                        }
                    )

                kernel_model = KernelModel(
                    **{
                        "name": "",  # A name uniquely identifies a a triple of kernel_configuration/commandline/kernel_source code
                        "description": kernel["description"],
                        "version": kernel["version"],
                        "commandline": kernel["command_line"],
                        "kernel_config": kernel["kernel_config"],
                        "kernel_source": kernel["kernel_source"],
                        "kernel_srcdir": kernel["kernel_srcdir"],
                        "image": kernel_image_model,
                        "uboot": uboot_model,
                        "default": kernel["is_default"],
                    }
                )

                kernel_models.append(kernel_model)

            triple_model = TripleModel(
                **{
                    "machine": os["machine"],
                    "os": os["os"],
                    "environment": os["environment"],
                }
            )

            os_model = OSModel(
                **{
                    "triple": triple_model,
                    "distribution": os["distribution"],
                    "release": os["release"],
                    "description": os["description"],
                    "sysroot": os["sysroot"],
                    "rootfs": os["rootfs"],
                    "multiarch": os["multiarch"],
                    "kernels": kernel_models,
                }
            )

            documentation_link_models = []

            for doc in docs:
                documentation_link_model = DocumentationLinkModel(
                    title=doc[0], loc=doc[1]
                )

                documentation_link_models.append(documentation_link_model)

            cpu_core_models = []

            for cpu_core in cpu_cores:
                # FIXME: Core Model DB?
                cpu_core_model = CoreModel(**cpu_core)

                cpu_core_models.append(cpu_core_model)

            ssh_connection_model = SSHConnectionModel(
                host=board["hostname"],
                username=board["ssh_username"],
                port=board["ssh_port"],
            )

            # FIXME: move to separate table
            board = dict(board)
            del board["ssh_username"]
            del board["ssh_port"]

            # FIXME: add database fields for rundir and board
            board_model = BoardModelDB(  # type: ignore
                **board,
                rundir="/home/es/run",
                board="unknown",
                doc=documentation_link_models,
                connections=[ssh_connection_model],
                cores=cpu_core_models,
                os=os_model,
            )

            board_models.append(board_model)

        return board_models

    def insert_board(
        self, board_model: BoardModel, additional_data: Any
    ) -> None:
        cpu_isas = set()
        cpu_implementers = set()
        cpu_uarchs = []
        cpu_extensions = set()

        for cpu_core in board_model.cores:
            cpu_isas.add(cpu_core.isa)
            cpu_implementers.add(cpu_core.vendor)
            cpu_uarchs.append(
                {
                    "id": cpu_core.uarch + cpu_core.vendor,
                    "name": cpu_core.uarch,
                    "vendor": cpu_core.vendor,
                }
            )
            cpu_extensions.update(cpu_core.extensions)

        query, bind_params = self.j.prepare_query(
            self.insert_board_query,
            {
                "soc_name": additional_data["soc_name"],
                "foundry_name": additional_data["foundry_name"],
                "technology": additional_data["technology"],
                "hostname": board_model.name,
                "board": board_model,
                "power_connector_name": additional_data["power_connector_name"],
                "voltage": additional_data["voltage"],
                "max_current": additional_data["voltage"],
                "cpu_isas": list(cpu_isas),
                "cpu_implementers": list(cpu_implementers),
                "cpu_uarchs": cpu_uarchs,
                "cpu_part_ids": additional_data["cpu_part_ids"],
            },
        )

        try:
            self.cursor.execute(query)
        except Exception as e:
            self.logger.error("ERROR: database import failed")
            self.logger.error(e)
