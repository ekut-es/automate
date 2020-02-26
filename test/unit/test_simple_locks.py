import getpass
import math
import shelve
import time

from automate.locks import SimpleLockManager


def test_simple_lock(tmpdir):
    db_file = tmpdir / "locks.db"
    lock_manager = SimpleLockManager(db_file, "test_user1")

    def get_timeout(board):
        with shelve.open(str(db_file)) as db:
            return db[board].timestamp

    lock_manager.lock("fake_board")
    assert lock_manager.has_lock("fake_board") == True
    assert lock_manager.is_locked("fake_board") == False
    lock_manager.unlock("fake_board")
    assert lock_manager.has_lock("fake_board") == False
    assert lock_manager.is_locked("fake_board") == False
    assert lock_manager.trylock("fake_board", "5m") == True
    assert abs(get_timeout("fake_board") - time.time() - 5 * 60) < 5
    assert lock_manager.trylock("fake_board", "5s") == True
    assert abs(get_timeout("fake_board") - time.time() - 5 * 60) < 5
    assert lock_manager.trylock("fake_board", "5h") == True
    assert abs(get_timeout("fake_board") - time.time() - 5 * 3600) < 5
    assert lock_manager.has_lock("fake_board") == True

    lock_manager2 = SimpleLockManager(db_file, "test_user2")

    assert lock_manager2.has_lock("fake_board") == False
    assert lock_manager2.is_locked("fake_board") == True
    assert lock_manager2.trylock("fake_board") == False
    assert lock_manager.unlock("fake_board") is None
    assert lock_manager2.trylock("fake_board") == True

    assert lock_manager2.unlock("fake_board") is None

    lock_manager2.lock("fake_board", "0")
    time.sleep(1.0)
    assert lock_manager2.has_lock("fake_board") == False
    assert lock_manager2.trylock("fake_board") == True
