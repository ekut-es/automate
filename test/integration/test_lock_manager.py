import time
from datetime import datetime, timedelta

import pytest
from db import db
from pytest import fixture

from automate.database import Database, database_enabled
from automate.locks import DatabaseLockManager, SimpleLockManager


@pytest.mark.skipif(not database_enabled(), reason="requires database drivers")
def test_lock_manager_db(db):
    local_lock_manager = DatabaseLockManager(db, "local")
    bobs_lock_manager = DatabaseLockManager(db, "bob")
    eves_lock_manager = DatabaseLockManager(db, "eve")

    do_test_lock_manager(
        local_lock_manager, eves_lock_manager, bobs_lock_manager
    )


def test_lock_manager_simple(tmp_path):
    lockfile = tmp_path / "locks.db"

    local_lock_manager = SimpleLockManager(lockfile, "local")
    bobs_lock_manager = SimpleLockManager(lockfile, "bob")
    eves_lock_manager = SimpleLockManager(lockfile, "eve")

    do_test_lock_manager(
        local_lock_manager, eves_lock_manager, bobs_lock_manager
    )


def do_test_lock_manager(
    local_lock_manager, eves_lock_manager, bobs_lock_manager
):
    board_name = "test_board"

    # nobody has a lock on test_board
    assert local_lock_manager.is_locked(board_name) == False
    assert bobs_lock_manager.is_locked(board_name) == False
    assert eves_lock_manager.is_locked(board_name) == False

    assert local_lock_manager.has_lock(board_name) == False
    assert bobs_lock_manager.has_lock(board_name) == False
    assert eves_lock_manager.has_lock(board_name) == False

    # nobody has a lock on test_board -> grant lock to local user for 5 sec
    assert local_lock_manager.trylock(board_name, "5") == True

    # eve and bob try to acquire the lock but wont get it
    assert eves_lock_manager.trylock(board_name, "5") == False
    assert bobs_lock_manager.trylock(board_name, "5") == False

    # local user releases the lock from test_board
    local_lock_manager.unlock(board_name)

    # nobody has a lock on test_board
    assert local_lock_manager.is_locked(board_name) == False
    assert bobs_lock_manager.is_locked(board_name) == False
    assert eves_lock_manager.is_locked(board_name) == False

    assert local_lock_manager.has_lock(board_name) == False
    assert bobs_lock_manager.has_lock(board_name) == False
    assert eves_lock_manager.has_lock(board_name) == False

    # nobody has a lock on test_board -> grant lock to bob for 5 sec
    assert bobs_lock_manager.trylock(board_name, "5") == True

    # local user and eve try to acquire the lock but wont get it
    assert local_lock_manager.trylock(board_name, "5") == False
    assert eves_lock_manager.trylock(board_name, "5") == False

    # bob extends lock by 10 sec
    assert bobs_lock_manager.trylock(board_name, "10") == True
