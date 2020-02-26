import getpass
import logging
import os
import shelve
import time
from collections import namedtuple
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from automate.board import Board


class LockManagerBase:
    """ Base Class for lock managers """

    def _do_unlock(self, board_name: str) -> None:
        raise NotImplemented("_do_unlock is not implemented")

    def _do_trylock(self, board_name: str, timeout: float) -> bool:
        raise NotImplemented("_do_trylock is not implemented")

    def _do_haslock(self, board_name) -> bool:
        raise NotImplemented("_do_haslock is not implemented")

    def _do_islocked(self, board_name) -> bool:
        raise NotImplemented("_do_haslock is not implemented")

    def _str_to_timedelta(self, inp: str) -> timedelta:
        inp = inp.strip()
        seconds = 0
        if inp[-1] == "h":
            seconds = int(inp[:-1].strip()) * 3600
        elif inp[-1] == "m":
            seconds = int(inp[:-1].strip()) * 60
        elif inp[-1] == "s":
            seconds = int(inp[:-1].strip())
        else:
            seconds = int(inp)

        delta = timedelta(seconds=seconds)

        return delta

    def lock(
        self, board: Union["Board", str], timeout: Union[timedelta, str] = "1h"
    ) -> None:
        if isinstance(board, str):
            board_name = board
        else:
            board_name = board.name

        if isinstance(timeout, str):
            delta = self._str_to_timedelta(timeout)
        else:
            delta = timeout

        timeout_absolute = datetime.now() + delta
        timeout_seconds = timeout_absolute.timestamp()

        while not self._do_trylock(board_name, timeout_seconds):
            time.sleep(0.5)

    def unlock(self, board: Union["Board", str]) -> None:

        if isinstance(board, str):
            board_name = board
        else:
            board_name = board.name

        if self._do_haslock(board_name):
            self._do_unlock(board_name)

    def trylock(
        self, board: Union["Board", str], timeout: Union[timedelta, str] = "1h"
    ) -> bool:
        if isinstance(board, str):
            board_name = board
        else:
            board_name = board.name

        if isinstance(timeout, str):
            delta = self._str_to_timedelta(timeout)
        else:
            delta = timeout

        timeout_absolute = datetime.now() + delta
        timeout_seconds = timeout_absolute.timestamp()

        return self._do_trylock(board_name, timeout_seconds)

    def has_lock(self, board: Union["Board", str]) -> bool:
        if isinstance(board, str):
            board_name = board
        else:
            board_name = board.name

        return self._do_haslock(board_name)

    def is_locked(self, board: Union["Board", str]) -> bool:
        if isinstance(board, str):
            board_name = board
        else:
            board_name = board.name

        return self._do_islocked(board_name)


LockEntry = namedtuple("LockEntry", ["user_id", "timestamp"])


class SimpleLockManager(LockManagerBase):
    """Simple lock manager using a gdbm shared file identifying lock holders by the username on the current machine"""

    def __init__(self, lockfile: Union[str, Path], user_id: str = "") -> None:
        self.lockfile = str(Path(lockfile).absolute())
        self.user_id = user_id
        if not user_id:
            self.user_id = getpass.getuser()

    def _do_unlock(self, board_name: str) -> None:
        with shelve.open(self.lockfile) as lockdb:
            if board_name in lockdb:
                if lockdb[board_name].user_id == self.user_id:
                    del lockdb[board_name]
        return None

    def _do_trylock(self, board_name: str, timeout: float) -> bool:
        timeout = float(timeout)
        with shelve.open(self.lockfile) as lockdb:
            current_timestamp = time.time()
            if board_name in lockdb:
                current_lock = lockdb[board_name]
                if current_lock.user_id != self.user_id:
                    if current_timestamp < current_lock.timestamp:
                        return False
                    else:
                        lockdb[board_name] = LockEntry(self.user_id, timeout)
                        return True

                if current_lock.timestamp < timeout:
                    lockdb[board_name] = LockEntry(self.user_id, timeout)
                return True

            lockdb[board_name] = LockEntry(self.user_id, timeout)
        return True

    def _do_haslock(self, board_name: str) -> bool:
        with shelve.open(self.lockfile) as lockdb:
            if board_name in lockdb:
                current_lock = lockdb[board_name]
                current_timestamp = time.time()

                if (
                    current_lock.user_id == self.user_id
                    and current_lock.timestamp > current_timestamp
                ):
                    return True

        return False

    def _do_islocked(self, board_name: str) -> bool:
        with shelve.open(self.lockfile) as lockdb:
            if board_name in lockdb:
                current_lock = lockdb[board_name]
                current_timestamp = time.time()
                if (
                    current_lock.user_id != self.user_id
                    and current_lock.timestamp > current_timestamp
                ):
                    return True

        return False
