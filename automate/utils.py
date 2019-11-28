from typing import Union

from .model.board import SSHConnectionModel, UARTConnectionModel


def connection_to_string(connection: Union[SSHConnectionModel, UARTConnectionModel]) -> str:
    table = {
        SSHConnectionModel: "ssh",
        UARTConnectionModel: "uart"
    }

    name = "UNKNOWN"

    t = type(connection)

    if t in table:
        name = table[t]

    return name
