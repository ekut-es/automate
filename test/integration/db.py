import os
from typing import Generator

import pytest
from pytest import fixture

from automate.database import Database, database_enabled


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
