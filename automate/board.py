import logging
from fabric import Connection


from contextlib import contextmanager


class BoardHandler(object):
    def __init__(self, board) -> None:
        self.logger = logging.getLogger(__name__)
        self.model = board

    @contextmanager
    def lock(self):
        self.logger.warning("Locking of boards is currently not implemented")

        try:
            # TODO: acqire lock
            yield None
        finally:
            # TODO: release lock
            pass

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
                        gw_host, user=gw_user, port=gw_port)

                c = Connection(host=host, user=user, port=port,
                               gateway=gateway_connection)
                return c

        raise Exception(
            "Could not find ssh connection for {}".format(self.model.id))
