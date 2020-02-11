import io
import os.path

from fabric import Connection
from pytest import raises, yield_fixture

import automate
from automate.config import AutomateConfig
from automate.context import AutomateContext
from fake_board import board, test_private_key

root_path = os.path.dirname(os.path.abspath(__file__))
metadata_path = os.path.join(root_path, "src", "metadata")


@yield_fixture()
def zynqberry_board():
    """Test fixture for zynqberry cross compiler"""

    config = AutomateConfig(lazy=True)
    config.automate.metadata = str(metadata_path)
    context = AutomateContext(config)

    board = context.board("zynqberry")
    if board and board.id == "zynqberry":
        return board

    raise Exception("Could not find zynqberry")


def test_fake_board(board, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO(""))

    host = board.host
    port = board.port
    user = "test"

    con = Connection(
        user=user,
        host=host,
        port=port,
        connect_kwargs={"key_filename": test_private_key},
    )
    con.open()

    assert con.is_connected == True

    print("ls /")
    con.run("ls /")


def test_zynqberry_board_has_builders(zynqberry_board):
    board = zynqberry_board

    make_builder = board.builder("make")
    cmake_builder = board.builder("cmake")
    kernel_builder = board.builder("kernel")

    assert isinstance(make_builder, automate.builder.MakefileBuilder)
    assert isinstance(cmake_builder, automate.builder.CMakeBuilder)
    assert isinstance(kernel_builder, automate.builder.KernelBuilder)
    with raises(Exception):
        zynqberry_cc.builder("unknown")
