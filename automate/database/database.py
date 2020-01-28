import inspect
import os
import pprint
import sys
from datetime import datetime
from os.path import dirname, join

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from jinjasql import JinjaSql

from automate.model import (
    BoardModel,
    CoreModel,
    DocumentationLinkModel,
    KernelImageModel,
    KernelModel,
    OSModel,
    SSHConnectionModel,
    TripleModel,
    UBootModel,
)


class Database:
    def __init__(self, host, port, db, user, password):
        self.connection_string = "host={} port={} dbname={} user={} password={}".format(
            host, port, database, user, password
        )

        try:
            connection = psycopg2.connect(self.connection_string)
            self.cursor = connection.cursor(
                cursor_factory=psycopg2.extras.DictCursor
            )
        except Exception as e:
            print(
                "ERROR: could not connnect to database: '"
                + self.connection_string
                + "'"
            )
            print(e)

        self.j = JinjaSql(param_style="pyformat")

        self.QUERIES_DIR = "queries"

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

    def __load_query(self, name):
        sql_file_path = self.QUERIES_DIR + "/" + name + ".sql"
        try:
            sql_file = open(sql_file_path, "r")
        except:
            print("ERROR: could not load sql file: '" + sql_file_path + "'")
        query = sql_file.read()
        return query

    def get_all_boards(self):
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
                        "id": 0,  # TODO what does id represent?
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
                    **{"title": doc["title"], "loc": doc["location"]}
                )

                documentation_link_models.append(documentation_link_model)

            cpu_core_models = []

            for cpu_core in cpu_cores:
                cpu_core_model = CoreModel(
                    **{
                        "id": cpu_core["os_id"],
                        "isa": cpu_core["isa"],
                        "uarch": cpu_core["uarch"],
                        "vendor": cpu_core["implementer"],
                        "extensions": cpu_core["extensions"],
                    }
                )

                cpu_core_models.append(cpu_core_model)

            ssh_connection_model = SSHConnectionModel(
                **{
                    "host": board["hostname"],
                    "username": board["ssh_username"],
                    "port": board["ssh_port"],
                }
            )

            board_model = BoardModel(
                **{
                    "model_file": "/dev/null",  # TODO remove
                    "model_file_mtime": datetime.strptime(
                        "2020-01-22 13:40:23", "%Y-%m-%d %H:%M:%S"
                    ),  # TODO remove
                    "name": board["name"],
                    "id": board["hostname"],
                    "board": board["hostname"],
                    "description": board["description"],
                    "rundir": "",  # TODO what is it?
                    "doc": documentation_link_models,
                    "connections": [ssh_connection_model],
                    "cores": cpu_core_models,
                    "os": os_model,
                }
            )

            board_models.append(board_model)

        return board_models

    def insert_board(self, board_model, additional_data):
        cpu_isas = set()
        cpu_implementers = set()
        cpu_uarchs = []
        cpu_extensions = set()

        for cpu_core in board_model.cores:
            cpu_isas.add(cpu_core.isa.value)
            cpu_implementers.add(cpu_core.vendor.value)
            cpu_uarchs.append(
                {
                    "id": cpu_core.uarch.value + cpu_core.vendor.value,
                    "name": cpu_core.uarch.value,
                    "vendor": cpu_core.vendor.value,
                }
            )
            cpu_extensions.update(cpu_core.extensions)

        cpu_uarchs = list({v["id"]: v for v in cpu_uarchs}.values())
        cpu_extensions = [x.value for x in cpu_extensions]

        query, bind_params = self.j.prepare_query(
            self.insert_board_query,
            {
                "soc_name": additional_data["soc_name"],
                "foundry_name": additional_data["foundry_name"],
                "technology": additional_data["technology"],
                "hostname": board_model.id,
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
            print("ERROR: database import failed")
            print(e)
