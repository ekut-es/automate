import os
from typing import Generator

import pytest
from pytest import fixture

from automate.database import Database, database_enabled
from automate.model import BoardModel, OSModel, TripleModel


@fixture
def db() -> Generator[Database, None, None]:
    database_object = Database(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        db=os.getenv("POSTGRES_DB", "der_schrank_test"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        user=os.getenv("POSTGRES_USER", "der_schrank_test"),
        password=os.getenv("POSTGRES_PASSWORD", "der_schrank_test"),
    )

    database_object.init()

    yield database_object


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
def test_lock(db):

    # no lock for 'test_board' has been aquired such that islocked == False
    assert not db.islocked("test_board")
