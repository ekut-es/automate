import automate.database as db

from pytest import fixture

@fixture
def database():
    database_object = db.Database(host="postgres",
                                  db="der_schrank_test",
                                  port=5432,
                                  user="der_schrank_test",
                                  password="der_schrank_test")
    
    return db

@pytest.mark.skipif(not db.database_enabled(),
                    reason="requires database drivers")
def test_database(database):
    assert database is not None
