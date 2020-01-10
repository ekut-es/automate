import logging
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, List, Union

from fabric import Connection

from automate.model.board import (
    CoreModel,
    OSModel,
    SSHConnectionModel,
    UARTConnectionModel,
)

from .compiler import CrossCompiler
from .model import BoardModel, CompilerModel
from .model.common import Toolchain


class Board(object):
    def __init__(
        self, board: BoardModel, compilers: List[CompilerModel], identity: str
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.model = board
        self.compiler_models = compilers
        self.identity = identity

    @contextmanager
    def lock(self):
        self.logger.warning("Locking of boards is currently not implemented")
        try:
            # TODO: acquire lock
            yield None
        finally:
            self.unlock()
            pass

    def unlock(self):
        self.logger.warning("Unlocking of boards is currently not implemented")

    def is_locked(self) -> bool:
        self.logger.warning("Locking is currently not implemented")

        return False

    def compiler(
        self, compiler_id: str = "", toolchain: Toolchain = Toolchain.GCC
    ) -> CrossCompiler:
        sorted_models = reversed(
            sorted(self.compiler_models, key=lambda x: x.version)
        )
        for compiler_model in sorted_models:
            if compiler_id != "":
                if compiler_id == compiler_model.id:
                    cc = CrossCompiler(compiler_model, self)
                    if cc.valid:
                        return cc
            else:
                cc = CrossCompiler(compiler_model, self)
                if cc.toolchain == toolchain and cc.valid:
                    return cc

        raise Exception(
            "Could not get compatible compiler with: id: '{}' and toolchain: '{}'".format(
                compiler_id, toolchain.value
            )
        )

    def compilers(
        self, toolchain: Union[Toolchain, None] = None
    ) -> List[CrossCompiler]:
        res = []
        for model in self.compiler_models:
            cc = CrossCompiler(model, self)
            if (cc.toolchain == toolchain) or (toolchain is None):
                if cc.valid:
                    res.append(cc)
        return res

    def connect(self, type: str = "ssh", timeout: int = 10) -> Connection:

        if type != "ssh":
            raise Exception("Currently only ssh connections are supported")

        for connection in self.model.connections:
            from .model import SSHConnectionModel

            if isinstance(connection, SSHConnectionModel):
                host = connection.host
                user = connection.username
                port = connection.port

                gateway_connection = None
                if self.model.gateway:
                    gw_host = self.model.gateway.host
                    gw_user = self.model.gateway.username
                    gw_port = self.model.gateway.port

                    gateway_connection = Connection(
                        gw_host,
                        user=gw_user,
                        port=gw_port,
                        connect_timeout=timeout,
                        connect_kwargs={"key_filename": self.identity},
                    )

                c = Connection(
                    host=host,
                    user=user,
                    port=port,
                    gateway=gateway_connection,
                    connect_timeout=timeout,
                    connect_kwargs={"key_filename": self.identity},
                )
                return c

        raise Exception(
            "Could not find ssh connection for {}".format(self.model.id)
        )

    def reboot(self, wait=True) -> Union[Connection, None]:
        """ Starts a new connection to the device and initiates a reboot

           If wait is true tries to start a new connection, 
           waits until connecting succeeds. And returns a new connection.
        """

        self.logger.info("Rebooting board {}".format(self.id))

        with self.connect() as connection:
            connection.run("sudo shutdown -r now & exit")

        self.logger.info("Reboot initiated!")
        time.sleep(3)

        if wait:
            return self.wait_for_connection()

        return None

    def wait_for_connection(self):
        self.logger.info("waiting for reconnection")
        connected = False
        while not connected:
            try:
                connection = self.connect()
                connection.open()
                return connection
            except Exception as e:
                self.logger.info("Waiting for reconnection")
                time.sleep(3)

    def reset(self, wait=True) -> Union[Connection, None]:
        self.logger.warning(
            "True resets are currently not implemented, trying a reboot instead"
        )
        try:
            self.reboot(wait=False)
        except BaseException as e:
            self.logger.error(
                "Reboot has been unsuccessful with exception {}".format(str(e))
            )
            self.logger.error("Please reboot device manually")

        if wait:
            return self.wait_for_connection()

        return None

    def homedir(self) -> Path:
        with self.connect() as con:
            result = con.run("echo $HOME", hide=True)
            return Path(result.stdout.strip())

    def kexec(
        self, kernel_id="", append="", commandline="", wait=True
    ) -> Union[Connection, None]:
        kernel_config = None

        for config in self.os.kernel:
            if kernel_id and kernel_id == config.id:
                kernel_config = config
            elif not kernel_id and config.default:
                kernel_config = config

        if kernel_config is None:
            raise Exception("Could not find kernel config")

        image = kernel_config.image
        if not commandline:
            commandline = kernel_config.commandline
        commandline = commandline + " " + append

        with self.connect() as con:
            with self.lock():
                con.run(
                    "sudo kexec -l {} --command-line='{}'".format(
                        image, commandline
                    )
                )
                con.run("sudo kexec -e && exit")

                if wait:
                    return self.wait_for_connection()

        return None

    def __getattr__(self, attr: str) -> Any:
        """proxy model properties if they are not shadowed by an own property"""
        return getattr(self.model, attr)
