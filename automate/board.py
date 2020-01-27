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
from .utils.kernel import KernelData


class Board(object):
    """ Automation Class for script based interaction with boards:

    Provides access to:
       - board data
       - board automation: upload, execution, reboot, reset, ...
       - board specific cross compilers
    """

    def __init__(
        self, board: BoardModel, compilers: List[CompilerModel], identity: str
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.model = board
        self.compiler_models = compilers
        self.identity = identity

    @contextmanager
    def lock_ctx(self, timeout: str = "1h"):
        if not self.has_lock():
            try:
                yield self.lock(timeout=timeout)
            finally:
                self.unlock()
        else:
            # Return a do nothing context manager
            try:
                yield None
            finally:
                pass

    def lock(self, timeout="1h"):
        self.logger.warning("Locking of boards is currently not implemented")
        if self.has_lock():
            return None
        else:
            # TODO: Aquire lock
            pass

    def has_lock(self) -> bool:
        return False

    def unlock(self):
        self.logger.warning("Unlocking of boards is currently not implemented")

    def trylock(self):
        return False

    def is_locked(self) -> bool:
        self.logger.warning("Locking is currently not implemented")

        return False

    def compiler(
        self, compiler_id: str = "", toolchain: Toolchain = Toolchain.GCC
    ) -> CrossCompiler:
        """ Build a Cross Compiler Object for this board 

        By default uses newest gcc compiler available in metadata.

        # Arguments
           compiler_id: use a specifc compiler id
           toolchain:  use newest configured compiler

        # Returns
           Object of class #automate.compiler.CrossCompiler configured to run builds for this board
        """

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
        """ Build list of cross compiler objects configured for this board

        # Arguments
        toolchain: Only build cross compilers from the given toolchain

        # Returns
        List of configured cross compilers
        """

        res = []
        for model in self.compiler_models:
            cc = CrossCompiler(model, self)
            if (cc.toolchain == toolchain) or (toolchain is None):
                if cc.valid:
                    res.append(cc)
        return res

    def connect(self, type: str = "ssh", timeout: int = 30) -> Connection:
        """
        Return a fabric.Connection to the board.

        # Arguments
        type: connection type currently only "ssh" is supportted
        timeout: timeout unitl connection should be established
        
        # Returns
        
        /fabric.Connection/ to the board

        """

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

        # Arguments
        wait: If wait is true tries to start a new connection, 
              waits until connecting succeeds, and returns a new connection.
        # Returns
        If wait was given a new connection is Returned
        """

        self.logger.info("Rebooting board {}".format(self.id))

        with self.connect() as connection:
            connection.run("sudo shutdown -r now & exit")

        self.logger.info("Reboot initiated!")
        time.sleep(3)

        if wait:
            return self.wait_for_connection()

        return None

    def wait_for_connection(self) -> Connection:
        """Wait until a successful ssh connection to the board can be established

        # Returns
        A new fabric.Connection object

        """

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
        """Hard-Reset the board

        TODO: Currently not implemented

        # Arguments
        wait: if true wait until the board is connectible again

        # Returns
        If wait was true a new Connection object
        """
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
        """ Return the home directory of the connected user 
        
        # Returns

        pathlib.Path: home directory
        """
        with self.connect() as con:
            result = con.run("echo $HOME", hide=True)
            return Path(result.stdout.strip())

    def kexec(
        self, kernel_id="", append="", commandline="", wait=True
    ) -> Union[Connection, None]:
        """ Start a board kernel using kexec 

        # Arguments
        kernel_id: id of the kernel to boot
        append: string of addition kernel commandline flags
        commandline: completely new kernel commandline
        wait: block unitl board is reachable via ssh again and reconnect
        
        # Returns
        if wait was given a new fabric.Connection is returned
        """
        kernel_config = None

        for config in self.os.kernels:
            if kernel_id and kernel_id == config.id:
                kernel_config = config
                break
            elif not kernel_id and config.default:
                kernel_config = config
                break

        if kernel_config is None:
            raise Exception("Could not find kernel config")

        if kernel_config.image is None:
            raise Exception("Could not find the kernel image entry")

        image = str(kernel_config.image.deploy_path)
        if not commandline:
            commandline = kernel_config.commandline
        commandline = commandline + " " + append

        with self.connect() as con:
            with self.lock_ctx():
                cmd = "sudo kexec -l {} --command-line='{}'".format(
                    image, commandline
                )

                self.logger.info("Running {}".format(cmd))
                con.run(cmd)

                cmd = (
                    "nohup bash -c 'sleep 1; sudo kexec -e' > /tmp/nohup.out &"
                )
                self.logger.info("Running {}".format(cmd))
                con.run(cmd)
                self.logger.info("Kexec executed")
                time.sleep(2.0)

                if wait:
                    self.logger.info("Waiting for reconnection")
                    return self.wait_for_connection()

        return None

    def kernel_data(self, id: str) -> Union[KernelData, None]:
        """ Information about the installed kernels 

        # Arguments
        id: kernel id for which information should be returned
        
        # Returns
        KernelData object for the kernel configration
        
        """

        for kernel_desc in self.os.kernels:
            if kernel_desc.id == id:
                return KernelData(self, kernel_desc)
        return None

    def __getattr__(self, attr: str) -> Any:
        """proxy model properties if they are not shadowed by an own property"""
        return getattr(self.model, attr)
