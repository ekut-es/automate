import logging
from fabric import Connection
from contextlib import contextmanager
from .compiler import CrossCompiler
from .model.common import Toolchain
from .model import BoardModel, CompilerModel
from typing import List


class Board(object):
    def __init__(
        self, board: BoardModel, compilers: List[CompilerModel]
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.model = board
        self.compiler_models = compilers

    @contextmanager
    def lock(self):
        self.logger.warning("Locking of boards is currently not implemented")

        try:
            # TODO: acquire lock
            yield None
        finally:
            # TODO: release lock
            pass

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

    def connect(self, type: str = "ssh") -> Connection:

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

                    gw_connection = Connection(
                        gw_host, user=gw_user, port=gw_port
                    )

                c = Connection(
                    host=host, user=user, port=port, gateway=gateway_connection
                )
                return c

        raise Exception(
            "Could not find ssh connection for {}".format(self.model.id)
        )

    def __getattr__(self, attr):
        """proxy model properties if they are not shadowed by an own property"""
        return getattr(self.model, attr)
