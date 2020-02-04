import logging
import os
import os.path
import sys
import time
from pathlib import Path
from typing import Any, List

import invoke
from fabric import Connection

from .board import Board
from .compiler import Compiler
from .config import AutomateConfig
from .database import Database, database_enabled
from .loader import ModelLoader
from .utils.network import connect


class AutomateContext(invoke.Context):
    def __init__(self, config: AutomateConfig):
        super(AutomateContext, self).__init__(config)

        self.logger = logging.getLogger(__name__)
        self.logger.debug("Context init")

        if hasattr(config.automate, "forwards") and config.automate.forwards:
            self._setup_forwards()
            pass
        database = None

        if hasattr(config.automate, "database") and config.automate.database:
            if database_enabled():
                self.logger.info("Setup database connection")
                database = Database(
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

    def _setup_forwards(self):
        for forward in self.config.automate.forwards:
            pidfile = (
                Path("/tmp") / f"automate_forward_{forward['local_port']}.pid"
            )
            if pidfile.exists():
                with pidfile.open() as pid_f:
                    pid = int(pid_f.read())
                    try:
                        os.kill(pid, 0)
                    except OSError as e:
                        pidfile.unlink()
                    else:
                        logging.debug("Forwarder process exists")
                        continue

            self.logger.info(
                f'forwarding {forward["local_port"]} to {forward["host"]}:{forward["remote_port"]}'
            )

            connection = connect(
                forward["host"],
                forward["user"],
                forward.get("port", 22),
                passwd_allowed=True,
            )

            print("Starting forwarder")

            # Detach from process using double fork
            pid = os.fork()
            if pid == 0:
                # os.setsid()
                pid = os.fork()
                if pid > 0:
                    os._exit(0)

                logging.debug("Forked forwarder %d", os.getpid())

                sys.stdout = pidfile.with_suffix(".stdout").open("w")
                sys.stderr = pidfile.with_suffix(".stderr").open("w")
                # sys.stdin = open("/dev/null")

                with pidfile.open("w") as pid_f:
                    pid_f.write(str(os.getpid()))

                connection = connect(
                    forward["host"],
                    forward["user"],
                    forward.get("port", 22),
                    passwd_allowed=True,
                )

                with connection:
                    with connection.forward_local(
                        local_port=forward["local_port"],
                        remote_port=forward["remote_port"],
                    ) as fw:
                        while True:
                            time.sleep(1.0)
                            print(connection)
                            sys.stdout.flush()

        time.sleep(1.0)
        logging.debug("Setup forwards finished")

    def boards(self):
        for board in self.metadata.boards:
            yield Board(
                self,
                board,
                self.metadata.compilers,
                os.path.expanduser(self.config.automate.identity),
            )

    def board(self, board_name: str) -> Board:
        for board in self.metadata.boards:
            if board.name == board_name:
                return Board(
                    self,
                    board,
                    self.metadata.compilers,
                    os.path.expanduser(self.config.automate.identity),
                )

        raise Exception(
            "Could not find board {} available boards {}".format(
                board_name, ",".join([board.name for board in self.metadata.boards])
            )
        )

    def compilers(self):
        for compiler in self.metadata.compilers:
            yield Compiler(self, compiler)

    def compiler(self, compiler_name: str) -> Compiler:

        for compiler in self.metadata.compilers:
            if compiler.name == compiler_name:
                return Compiler(self, compiler)

        raise Exception(
            "Could not find compiler {} available compilers {}".format(
                compiler_name,
                ",".join([compiler.name for compiler in self.metadata.compilers]),
            )
        )
