import pytest
from pytest import fixture

from automate.database import Database, database_enabled


@fixture
def db():
    database_object = Database(
        host="localhost",
        db="der_schrank_test",
        port=5432,
        user="der_schrank_test",
        password="der_schrank_test",
    )

    yield database_object


@pytest.mark.skipif(not database_enabled(), reason="requires database drivers")
def test_database(db):
    assert db is not None


@pytest.mark.skipif(not database_enabled(), reason="requires database drivers")
def test_database_init(db):
    assert db is not None

    db.init()

    cursor = db.cursor

    cursor.execute(
        "select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';"
    )

    print(cursor)
