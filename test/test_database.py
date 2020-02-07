import pytest
from pytest import fixture

from automate.database import Database, database_enabled


@fixture
def db():
    database_object = Database(
        host="postgres",
        db="der_schrank_test",
        port=5432,
        user="der_schrank_test",
        password="der_schrank_test",
    )

    return database_object


@pytest.mark.skipif(not database_enabled(), reason="requires database drivers")
def test_database(db):
    assert db is not None


@pytest.mark.skipif(not database_enabled(), reason="requires database drivers")
def test_database_init(db):
    assert database is not None

    db.init()
