import concurrent.futures
import contextlib
import gzip
import io
import logging
import os.path
import random
import re
import shlex
import shutil
import socket
import subprocess
import tempfile
import threading
import time
from pathlib import Path

from fabric import task
from patchwork.files import exists

from ..utils import fix_symlinks
from ..utils.network import find_local_port, rsync


@task
def run(c, board, command, cwd=""):  # pragma: no cover
    """Run command remotely
    
        -b/--board: target board id
        -c/--command: command to run
        --cwd: working directory of the command
    """

    bh = c.board(board)

    if not cwd:
        cwd = bh.model.rundir

    with bh.connect() as con:
        con.run("mkdir -p {}".format(str(cwd)))
        with con.cd(str(cwd)):
            con.run(command)


@task
def put(c, board, file, remote_path=""):  # pragma: no cover
    """Put file on the board
     
        -b/--board: target board id
        -f/--file: local file
        -r/--remote: remote file path (default is board specific rundir)
    """

    bh = c.board(board)
    with bh.connect() as con:
        if not remote_path:
            remote_path = bh.model.rundir
            remote_file = remote_path / Path(file).name

        else:
            remote_file = Path(remote_path)

        logging.info(
            "Putting %s to %s:%s", str(file), str(board), str(remote_file)
        )
        con.run("mkdir -p {}".format(str(remote_file.parent)))
        con.put(str(file), str(remote_file))


@task
def get(c, board, remote, local=""):  # pragma: no cover
    """Get file from board
       
        -b/--board: target board id
        -r/--remote: remote file path
        -l/--local:  local folder or filename (default is current working directory)
    """

    bh = c.board(board)
    with bh.connect() as con:
        if local:
            local_path = Path(local)
            if local_path.is_dir():
                local_path.mkdir(parents=True, exist_ok=True)
            else:
                local_path.parent.mkdir(parents=True, exist_ok=True)

        con.get(remote=str(remote), local=str(local))


@task
def lock(c, board, timeout="1h"):  # pragma: no cover
    """Lock board

        -b/--board: target board id
        -t/--timeout: timeout for the lock
    """
    board = c.board(board)
    board.lock(timeout=timeout)


@task
def unlock(c, board):  # pragma: no cover
    """Unlock board

       -b/--board: target board id 
    """
    board = c.board(board)
    board.unlock()


@task
def is_locked(c, board):  # pragma: no cover
    """Return 0 if board is locked by other user

       -b/--board: target board id 
    """
    board = c.board(board)
    if board.is_locked():
        return 0

    return 1


@task
def has_lock(c, board):  # pragma: no cover
    """Return 0 if board is locked by current user

       -b/--board: target board id 
    """
    board = c.board(board)
    if board.has_lock():
        return 0

    return 1


@task
def reboot(c, board, wait=False):  # pragma: no cover
    """Reboot  board
       
        -b/--board: target board id
        -w/--wait block until the board is reachable via ssh again
    """

    board = c.board(board)
    board.reboot(wait)


@task
def reset(c, board, wait=False):  # pragma: no cover
    """Hard reset board
       
        -b/--board: target board id
        -w/--wait: block until the board is reachable again
    """

    board = c.board(board)
    board.reset(wait)


@task
def install(c, board, package):  # pragma: no cover
    """Install a package on the board

        -b/--board: target board id
        -p/--package: package
    """

    board = c.board(board)

    # TODO: Support other distributions as needed
    if board.os.distribution not in ["debian", "ubuntu"]:
        logging.error(
            "Currently package installation only supports Ubuntu or Debian based systems this board is {}".format(
                board.os.distribution
            )
        )
        return -1

    apt = "DEBIAN_FRONTEND=noninteractive sudo apt-get install -y {0}"
    with board.connect() as con:
        con.run(apt.format(package))

    return 0


@task
def shell(c, board):  # pragma: no cover
    """Start a remote shell 

        -b/--board: target board id
    """

    board = c.board(board)

    with board.connect() as con:
        con.run("$SHELL", pty=True)


@task
def board_ids(c, filter=""):  # pragma: no cover
    """returns list of board_ids suitable for usage in shell scripts
    
       -f/--filter: filter expression for boards

               Filter expression is prepended with 'lambda board:  ' and then evaluated as a python function
               board is an object of class Board, only returns board_ids if filter expression is true

               Examples:
 
               board.machine == 'zynqberry' to only run on zynqberry boards

               board.trylock() to only iterate over boards that are currently unlocked, and lock the boards while iterating
    """

    if filter:
        filter = "lambda board: " + filter
        filter = eval(filter)
    else:
        filter = lambda board: True

    for board in (board for board in c.boards() if filter(board)):
        print(board.id)


@task
def rsync_to(c, board, source, target="", delete=False):  # pragma: no cover
    """rsync a folder to the target board by default the 
    
       
       -b/--board: target board id
       -s/--source: source folder/file
       -t/--target: target folder/file default is configured rundir on the board
       -d/--delete: delete files from target that do not exist in the source 
    """
    board = c.board(board)

    if not target:
        target = str(board.rundir) + "/"
    elif target[0] != "/":
        target = os.path.join(board.rundir, target)

    with board.connect() as con:
        rsync(con, source=source, target=target, delete=delete)


@task
def kexec(
    c, board, kernel_id="", append="", commandline="", wait=False
):  # pragma: no cover
    """Start the Linux kernel using kexec
    
       -b/--board: target board id
       -k/--kernel-id: target kernel id
       -a/--append: Append the given string to the commandline
       -w/--wait: wait until board is reachable via ssh again
    """

    board = c.board(board)

    board.kexec(kernel_id, append, commandline, wait=wait)
