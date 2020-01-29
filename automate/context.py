import logging
import os.path
from typing import Any, List

import invoke
from fabric import Connection
from paramiko.ssh_exception import AuthenticationException
from prompt_toolkit import prompt

from .board import Board
from .compiler import Compiler
from .config import AutomateConfig
from .database import Database, database_enabled
from .loader import ModelLoader


class AutomateContext(invoke.Context):
    def __init__(self, config: AutomateConfig):
        super(AutomateContext, self).__init__(config)

        self.logger = logging.getLogger(__name__)
        self.logger.debug("Context init")

        self.forward_connections: List[Connection] = []
        if hasattr(config.automate, "forwards") and config.automate.forwards:
            # self._setup_forwards()
            pass
        database = None

        if hasattr(config.automate, "database") and config.automate.database:
            if database_enabled():
                self.logger.info("Setup database connection")
                self.database = Database(
                    self.config.automate.database.host,
                    self.config.automate.database.port,
                    self.config.automate.database.db,
                    self.config.automate.database.user,
                    self.config.automate.database.password,
                )
            else:
                self.logger.warning(
                    "You have configured a database but the required "
                )

        loader = ModelLoader(config, database=database)
        self.metadata = loader.load()

    def __del__(self):
        for connection in self.forward_connections:
            connection.close()

    def _setup_forwards(self):
        for forward in self.config.automate.forwards:
            self.logger.info(
                f'forwarding {forward["local_port"]} to {forward["host"]}:{forward["remote_port"]}'
            )
            try:
                connection = Connection(forward["host"], user=forward["user"])
                connection.open()
            except AuthenticationException as e:
                password = prompt(
                    "Password for {}@{}: ".format(
                        forward["user"], forward["host"]
                    ),
                    is_password=True,
                )
                connection = Connection(
                    user=forward["user"],
                    host=forward["host"],
                    connect_kwargs={"password": password},
                )
                connection.open()

            connection.forward_local(
                local_port=forward["local_port"],
                remote_port=forward["remote_port"],
            )
            self.forward_connections.append(connection)

    def boards(self):
        for board in self.metadata.boards:
            yield Board(
                board,
                self.metadata.compilers,
                os.path.expanduser(self.config.automate.identity),
            )

    def board(self, board_id: str) -> Board:
        for board in self.metadata.boards:
            if board.id == board_id:
                return Board(
                    board,
                    self.metadata.compilers,
                    os.path.expanduser(self.config.automate.identity),
                )

        raise Exception(
            "Could not find board {} available boards {}".format(
                board_id, ",".join([board.id for board in self.metadata.boards])
            )
        )

    def compilers(self):
        for compiler in self.metadata.compilers:
            yield Compiler(compiler)

    def compiler(self, compiler_id: str) -> Compiler:

        for compiler in self.metadata.compilers:
            if compiler.id == compiler_id:
                return Compiler(compiler)

        raise Exception(
            "Could not find compiler {} available compilers {}".format(
                compiler_id,
                ",".join([compiler.id for compiler in self.metadata.compilers]),
            )
        )
