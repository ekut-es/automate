import time
from typing import Generator

import pytest
from db import db
from pytest import fixture

from automate.database import Database, database_enabled
from automate.model import BoardModel, OSModel, TripleModel


@fixture
def test_boards() -> Generator[BoardModel, None, None]:
    test_os = OSModel(
        triple=TripleModel(machine="arm", os="linux", environment="gnueabihf"),
        distribution="test_distribution",
        description="Test Data",
        release="18.4",
    )
    test_board = BoardModel(
        name="test_board",
        rundir="/home/es/run",
        board="test_board",
        description="Fake test board",
        connections=[],
        cores=[],
        os=test_os,
    )

    yield test_board


@pytest.mark.skipif(not database_enabled(), reason="requires database drivers")
def test_database(db):
    assert db is not None
    assert db.cursor is not None


@pytest.mark.skipif(not database_enabled(), reason="requires database drivers")
def test_database_init(db):
    assert db is not None

    db.init()

    cursor = db.cursor

    cursor.execute(
        "select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';"
    )

    result = cursor.fetchall()

    result = [item for sublist in result for item in sublist]

    assert "docs" in result
    assert "os_kernels" in result
    assert "board_oss" in result
    assert "distributions" in result
    assert "environments" in result
    assert "machines" in result
    assert "oss" in result
    assert "board_cpu_core_extensions" in result
    assert "board_cpu_cores" in result
    assert "cpu_uarch_implementations" in result
    assert "cpu_uarchs" in result
    assert "cpu_implementers" in result
    assert "cpu_isas" in result
    assert "boards" in result
    assert "power_connectors" in result
    assert "socs" in result
    assert "foundries" in result


@pytest.mark.skipif(not database_enabled(), reason="requires database drivers")
def test_initial_database_has_no_boards(db):

    boards = db.get_all_boards()
    assert boards == []


@pytest.mark.skipif(not database_enabled(), reason="requires database drivers")
def test_database_insert_board(db):

    boards = db.get_all_boards()
    assert boards == []


@pytest.mark.skipif(not database_enabled(), reason="requires database drivers")
def test_database_locks(db):

    board_name = "test_board"

    # nobody has a lock on test_board
    assert db.islocked(board_name, "alice") == False

    # alice should not have a lock on test_board
    assert db.haslock(board_name, "alice") == False

    # nobody has a lock on test_board -> grant lock to alice for 5 sec
    assert db.trylock(board_name, "alice", 5) == True

    # eve tries to acquire the lock but wont get it
    assert db.trylock(board_name, "eve", 5) == False

    # alice releases the lock from test_board
    db.unlock(board_name, "alice")

    # nobody has a lock on test_board
    assert db.islocked(board_name, "eve") == False

    # nobody has a lock on test_board -> grant lock to bob for 5 sec
    assert db.trylock(board_name, "bob", 5) == True

    # eve tries to acquire the lock but wont get it
    assert db.trylock(board_name, "eve", 5) == False

    # bob extends lock by 10 sec
    assert db.trylock(board_name, "bob", 10) == True

    time.sleep(6)

    # eve tries to acquire the lock but wont get it
    assert db.trylock(board_name, "eve", 5) == False

    time.sleep(10)

    # lock on test_board for bob has expired
    assert db.islocked(board_name, "alice") == False

    # lock on test_board for bob has expired -> grant lock to alice for 5 sec
    assert db.trylock(board_name, "alice", 5) == True

    # alice releases the lock from test_board
    db.unlock(board_name, "alice")

    # nobody has a lock on test_board
    assert db.islocked(board_name, "horst") == False
