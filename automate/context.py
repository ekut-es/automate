import logging
import os
import os.path
import socket
import sys
import time
from typing import Generator, Optional, Union

import invoke
from setproctitle import setproctitle

from .board import Board
from .compiler import Compiler
from .config import AutomateConfig
from .database import Database, database_enabled
from .loader import ModelLoader
from .model.common import Toolchain
from .utils.appdirs import runtime_dir
from .utils.network import connect


class AutomateContext(invoke.Context):
    """ Main entry for interaction with the system"""

    def __init__(self, config: AutomateConfig) -> None:
        """Setup context
        
           # Arguments:
           config: Automate Configuration for the System
        """
        super(AutomateContext, self).__init__(config)

        self.logger = logging.getLogger(__name__)

        if hasattr(config.automate, "forwards") and config.automate.forwards:
            self._setup_forwards()

        self.database: Optional[Database] = None

        self._setup_database()

        loader = ModelLoader(config)  # , database=self.database)
        self.metadata = loader.load()

    def _setup_database(
        self,
    ) -> Optional[Database]:  # Setup database connections
        config = self.config
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
                    "You have configured a database but the required packages are not installed"
                )
        return None

    def _setup_forwards(
        self,
    ) -> None:  # Start forwarder processes for port forwarding if corresponding processes do not exist already

        new_forwarder_started = False
        for forward in self.config.automate.forwards:
            pidfile = (
                runtime_dir() / f"automate_forward_{forward['local_port']}.pid"
            )
            socketfile = (
                runtime_dir() / f"automate_forward_{forward['local_port']}.sock"
            )
            if pidfile.exists():
                self.logger.info("Pidfile exists")
                with pidfile.open() as pid_f:
                    pid = int(pid_f.read())
                    try:
                        os.kill(pid, 0)
                    except OSError:
                        pidfile.unlink()
                        if socketfile.exists():
                            socketfile.unlink()
                    else:
                        logging.info("Forwarder process exists")
                        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                        try:
                            sock.connect(str(socketfile).encode("utf-8"))
                        except socket.error:
                            raise Exception(
                                f"Could not connect to forwarder socket {str(socketfile)} please kill forwarder process  {pid}"
                            )

                        current_remote_port = ""
                        try:
                            self.logger.info("Requesting remote port")
                            # Send data
                            message = "remote_port\n"
                            sock.sendall(message.encode("utf-8"))

                            data = ""

                            while len(data) == 0 or data[-1] != "\n":
                                data += sock.recv(16).decode("utf-8")
                            current_remote_port = data.strip()
                        except:
                            self.logger.warning(
                                "Execption during remote handler setup"
                            )
                        finally:
                            sock.close()

                        self.logger.info(
                            "Received remote port: %s", current_remote_port
                        )

                        if forward["remote_port"] == int(current_remote_port):
                            continue
                        else:
                            self.logger.info(
                                "Remote ports did not match actual: %s expected: %s",
                                current_remote_port,
                                forward["remote_port"],
                            )
                            os.kill(pid, 9)
            else:
                self.logger.info("Pidfile does not exist %s", str(pidfile))

            new_forwarder_started = True
            self.logger.info(
                f'forwarding {forward["local_port"]} to {forward["host"]}:{forward["remote_port"]}'
            )

            connection = connect(
                forward["host"],
                forward["user"],
                forward.get("port", 22),
                passwd_allowed=True,
            )

            # Detach from process using double fork
            pid = os.fork()
            if pid == 0:
                os.setsid()
                pid = os.fork()
                if pid > 0:
                    os._exit(0)

                setproctitle(
                    f"automate-forward {forward['local_port']} {forward['remote_port']}"
                )

                logging.info("Forked forwarder %d", os.getpid())

                sys.stdout = pidfile.with_suffix(".stdout").open("w")
                sys.stderr = pidfile.with_suffix(".stderr").open("w")

                with pidfile.open("w") as pid_f:
                    pid_f.write(str(os.getpid()))

                if socketfile.exists():
                    socketfile.unlink()

                server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                server_sock.bind(str(socketfile).encode("utf-8"))
                server_sock.listen(1)

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
                    ):
                        while True:
                            client_socket, client_address = server_sock.accept()
                            command = ""
                            while len(command) == 0 or command[-1] != "\n":
                                command += client_socket.recv(16).decode(
                                    "utf-8"
                                )
                            command = command.strip()

                            if command == "remote_port":
                                client_socket.sendall(
                                    f'{forward["remote_port"]}\n'.encode(
                                        "utf-8"
                                    )
                                )
                            elif command == "local_port":
                                client_socket.sendall(
                                    f'{forward["local_port"]}\n'.encode("utf-8")
                                )
                            elif command == "shutdown":
                                client_socket.sendall("ok\n".encode("utf-8"))
                            else:
                                client_socket.sendall(
                                    "error: unknown command".encode("utf-8")
                                )

                            client_socket.close()
        if new_forwarder_started:
            logging.info("Waiting for forwarder setup")
            time.sleep(1.0)

        logging.debug("Setup forwards finished")

    def boards(self) -> Generator[Board, None, None]:
        """Return iterator over Boards"""
        for board in sorted(self.metadata.boards, key=lambda b: b.name):
            yield Board(
                self,
                board,
                self.metadata.compilers,
                os.path.expanduser(self.config.automate.identity),
            )

    def board(self, board_name: str) -> Board:
        """Return Board object for board identified by board_name
        
           #Returns
           Board object if board exists
        """
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
                board_name,
                ",".join([board.name for board in self.metadata.boards]),
            )
        )

    def compilers(self,) -> Generator[Compiler, None, None]:
        """ Return iterator over configured compilers  """
        for compiler in sorted(
            self.metadata.compilers,
            key=lambda c: (c.toolchain.value, c.version),
        ):

            yield Compiler(self, compiler)

    def compiler(
        self,
        compiler_name: str = "",
        toolchain: Union[Toolchain, str] = Toolchain.GCC,
    ) -> Compiler:
        """
        Return Compiler object for Compiler identified by compiler_name,
        or newest compiler from toolchain if compiler_name is empty
        """

        if compiler_name:
            for compiler in self.metadata.compilers:
                if compiler.name == compiler_name:
                    return Compiler(self, compiler)

        if isinstance(toolchain, str):
            toolchain = Toolchain(toolchain)

        for compiler in reversed(
            sorted(self.metadata.compilers, key=lambda x: x.version)
        ):
            if compiler.toolchain == toolchain:
                return Compiler(self, compiler)

        raise Exception(
            "Could not find compiler {} available compilers {}".format(
                compiler_name,
                ",".join(
                    [compiler.name for compiler in self.metadata.compilers]
                ),
            )
        )
