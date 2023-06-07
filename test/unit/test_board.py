import io
import os.path

from fabric import Connection
from fake_board import fake_board, test_private_key
from monkeypatch_state import monkeypatch_state
from pytest import fixture, raises

import automate
from automate.config import AutomateConfig
from automate.context import AutomateContext

root_path = os.path.dirname(os.path.abspath(__file__))
metadata_path = os.path.join(root_path, "src", "metadata")


@fixture()
def zynqberry_board(monkeypatch):
    """Test fixture returning a faked zynqberry board,
    .connect method is monkeypatched and does produce a FakeConnection object
    """

    class FakeConnection:
        def __init__(self):
            self.commands = []

        def __enter__(self, *args, **kwargs):
            return self

        def __exit__(*args, **kwargs):
            pass

        def open(self):
            pass

        @property
        def is_connected(self):
            return True

        def run(self, command, hide=[], warn=False):
            self.commands.append(command)

    fake_connection = FakeConnection()

    def get_fake_connection(*args, **kwargs):
        print("Fake connection: ", fake_connection)
        return fake_connection

    monkeypatch.setattr(automate.Board, "connect", get_fake_connection)

    config = AutomateConfig(lazy=True)
    config.automate.boardroot = "/tmp"
    config.automate.metadata = str(metadata_path)
    context = AutomateContext(config)

    board = context.board("zynqberry")
    if board and board.id == "zynqberry":
        return board

    raise Exception("Could not find zynqberry")


def test_fake_board_connection(fake_board, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO(""))

    connection = fake_board.connect()
    assert connection.is_connected
    connection.run("ls")


def test_fake_board_nested_connection(fake_board, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    with fake_board.connect() as con:
        with fake_board.connect() as con2:
            assert con.is_connected
            assert con2.is_connected

            assert con == con2

        assert con.is_connected


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


def test_board_compiler(zynqberry_board):
    board = zynqberry_board

    compiler = board.compiler()

    assert compiler.name == "aarch32hf-gcc74"
    assert compiler.cflags == "-mcpu=cortex-a9 -O2"
    assert compiler.ldflags == "-mcpu=cortex-a9 -O2"
    assert compiler.libs == ""

    compiler.configure(uarch_opt=False)

    assert compiler.cflags == "-march=armv7-a -O2"
    assert compiler.ldflags == "-march=armv7-a -O2"

    compiler.configure(uarch_opt=False, isa_opt=False)

    assert compiler.cflags == "-O2"
    assert compiler.ldflags == "-O2"

    compiler.configure(flags="", uarch_opt=False, isa_opt=False)

    assert compiler.cflags == ""
    assert compiler.ldflags == ""


def test_board_compilers(zynqberry_board):
    board = zynqberry_board

    from automate.model import Toolchain

    compilers = board.compilers(toolchain=Toolchain.GCC)
    assert len(compilers) == 1
    assert compilers[0].name == "aarch32hf-gcc74"

    compilers = board.compilers()
    assert len(compilers) == 4


def test_board_reboot(zynqberry_board):

    fake_connection = zynqberry_board.connect()
    assert fake_connection is not None

    zynqberry_board.reboot()

    assert "shutdown -r now" in fake_connection.commands[0]


def test_board_reset(zynqberry_board):

    fake_connection = zynqberry_board.connect()
    assert fake_connection is not None

    zynqberry_board.reset()

    assert "shutdown -r now" in fake_connection.commands[0]


def test_board_kexec(zynqberry_board):

    fake_connection = zynqberry_board.connect()
    assert fake_connection is not None

    zynqberry_board.kexec()

    assert "kexec -l" in fake_connection.commands[0]
    assert "kexec -e" in fake_connection.commands[1]
