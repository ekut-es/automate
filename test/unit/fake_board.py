import os

import mockssh
from pytest import yield_fixture

from automate import Board
from automate.model import (
    BoardModel,
    CoreModel,
    OSModel,
    SSHConnectionModel,
    TripleModel,
)

root_path = os.path.dirname(os.path.abspath(__file__))
test_private_key = os.path.join(root_path, "fake_board_data", "test_id_rsa")
test_public_key = os.path.join(root_path, "fake_board_data", "test_id_rsa.pub")


@yield_fixture()
def fake_board():
    users = {"test": str(test_private_key)}
    with mockssh.Server(users) as s:
        board_model = BoardModel(
            name="fake_board",
            board="board",
            description="Mocked Board to test SSH Connections",
            rundir="/run",
            connections=[
                SSHConnectionModel(host=s.host, username="test", port=s.port)
            ],
            cores=[],
            os=OSModel(
                triple=TripleModel(
                    machine="arm",
                    vendor="linaro",
                    os="linux",
                    environment="gnueabihf",
                ),
                distribution="fake distro",
                release="2020.1",
                description="Fake Distribution for testing purposes",
            ),
        )

        board = Board(None, board_model, [], identity=test_private_key)

        yield board
