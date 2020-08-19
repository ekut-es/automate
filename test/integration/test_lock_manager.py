import pytest
from pytest import fixture

from automate.database import Database, database_enabled
from automate.locks import LockManager
from datetime import datetime, timedelta

from db import db

@pytest.mark.skipif(not database_enabled(), reason="requires database drivers")
def test_lock_manager(db):
   
    board_name = "test_board"

    local_lock_manager = LockManager(db)
    bobs_lock_manager = LockManager(db, "bob")
    eves_lock_manager = LockManager(db, "eve")

    # nobody has a lock on test_board 
    assert not local_lock_manager.is_locked(board_name)
    assert not bobs_lock_manager.is_locked(board_name)
    assert not eves_lock_manager.is_locked(board_name)

#assert local_lock_manager.trylock(board_name, timedelta(seconds=5))

    # alice should not have a lock on test_board
#assert not db.haslock("test_board", "alice")

    # nobody has a lock on test_board -> grant lock to alice for 5 sec
#assert db.trylock("test_board", "alice", 5)

    # eve tries to acquire the lock but wont get it
#assert not db.trylock("test_board", "eve", 5)

    # alice releases the lock from test_board
#db.unlock("test_board", "alice")

    # nobody has a lock on test_board 
#assert not db.islocked("test_board")

    # nobody has a lock on test_board -> grant lock to bob for 5 sec
#assert db.trylock("test_board", "bob", 5)

    # eve tries to acquire the lock but wont get it
#assert not db.trylock("test_board", "eve", 5)

    # bob extends lock by 10 sec 
#assert db.trylock("test_board", "bob", 10)

#time.sleep(6)

    # eve tries to acquire the lock but wont get it
#assert not db.trylock("test_board", "eve", 5)

#time.sleep(6)

    # lock on test_board for bob has expired
#assert not db.islocked("test_board")

    # lock on test_board for bob has expired -> grant lock to alice for 5 sec
#assert db.trylock("test_board", "alice", 5)

    # alice releases the lock from test_board
#db.unlock("test_board", "alice")

    # nobody has a lock on test_board 
#assert not db.islocked("test_board")

