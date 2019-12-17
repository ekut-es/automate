import concurrent.futures
import contextlib
import gzip
import io
import logging
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
def safe_rootfs(c, board):  # pragma: no cover
    "Safe rootfs image of board to board directory"
    bh = c.board(board)

    port = find_local_port()

    image_name = Path(bh.os.rootfs)
    image_name.parent.mkdir(parents=True, exist_ok=True)

    print("Cloning rootfs to {}\n".format(image_name))

    with bh.lock():

        logging.info("Connecting to target using port {}".format(port))

        con = bh.connect()

        con.run("uptime")

        result = con.run(
            "echo 1 | sudo tee /proc/sys/kernel/sysrq", hide="stdout", pty=True
        )
        if result.return_code != 0:
            raise Exception("Could not enable sysrq triggers")

        mount_result = con.run("mount", hide="stdout")
        if mount_result.return_code != 0:
            raise Exception("Could not get mountpoints")
        mount_output = mount_result.stdout
        mount_table_pattern = re.compile(r"(.*) on (.*) type (.*) \((.*)\)")
        rootdevice = ""
        for line in mount_output.splitlines():
            line = line.strip()
            match = re.match(mount_table_pattern, line)
            if match:
                device = match.group(1).strip()
                mountpoint = match.group(2).strip()
                fstype = match.group(3).strip()
                args = match.group(4).strip()

                if mountpoint == "/":
                    rootdevice = device
                    break

        if not rootdevice:
            raise Exception("Could not find root device for {}".format(board))

        logging.info("Using device: {}".format(rootdevice))

        with concurrent.futures.ThreadPoolExecutor() as thread_executor:
            try:
                with open(image_name.with_suffix(".tmp"), "wb") as image_file:
                    logging.info("Starting listener")

                    def reader_func():

                        reader_cmd = "nc -l {}".format(port)
                        reader = subprocess.Popen(
                            shlex.split(reader_cmd), stdout=subprocess.PIPE
                        )

                        decompressor = gzip.GzipFile(
                            fileobj=reader.stdout, mode="rb"
                        )
                        shutil.copyfileobj(decompressor, image_file)
                        return reader.wait()

                    reader_result = thread_executor.submit(reader_func)

                    result = con.run(
                        "echo u | sudo tee /proc/sysrq-trigger",
                        hide="stdout",
                        pty=True,
                    )
                    if result.return_code != 0:
                        raise Exception(
                            "Could not remount file systems read only"
                        )

                    with con.forward_remote(port):
                        logging.info("Starting writer")
                        res = con.run(
                            "sudo dd if={} | gzip -c |nc -N localhost {}".format(
                                rootdevice, port
                            ),
                            pty=True,
                        )

                        logging.info("waiting for reader")

                        result = reader_result.result()
                        if result != 0:
                            raise Exception("Could not write image!")

            except BaseException as e:
                if image_name.with_suffix(".tmp").exists():
                    c.run("rm {}".format(image_name.with_suffix(".tmp")))
                logging.error(
                    "Exception during image writing: {}".format(str(e))
                )
            finally:
                logging.info("Rebooting target {}".format(board))
                bh.reboot(wait=False)

        logging.info("Sparsifying saved image")
        c.run("fallocate -d {0}".format(image_name.with_suffix(".tmp")))
        if image_name.exists():
            c.run(
                "mv {0} {1}".format(image_name, image_name.with_suffix(".bak"))
            )

        logging.info("Moving image to result")
        c.run("mv {0} {1}".format(image_name.with_suffix(".tmp"), image_name))
        print("Finished image saving.")

        return 0


@task
def build_sysroot(c, board):  # pragma: no cover
    "Build a sysroot for the given board"

    bh = c.board(board)

    image_path = Path(bh.os.rootfs)
    if not image_path.exists():
        safe_rootfs(c, board)

    try:
        tmp_path = Path(tempfile.mkdtemp())
        logging.debug("Using mountpoint {}".format(tmp_path))

        c.run("sudo mount -l {} {}".format(str(image_path), str(tmp_path)))

        bh.os.sysroot.mkdir(exist_ok=True, parents=True)

        try:
            rsync_result = c.run(
                r'rsync -ar --delete --delete-excluded --exclude="/tmp" --exclude="/home" {}/ {}/'.format(
                    str(tmp_path), str(bh.os.sysroot)
                ),
                hide="stdout",
                warn=True,
            )

            fix_symlinks(bh.os.sysroot)

        except BaseException as e:
            print(e)
            raise e
        finally:
            c.run("sudo umount {}".format(tmp_path))

    except BaseException as e:
        print(e)
        raise e
    finally:
        c.run("sudo rmdir {}".format(tmp_path))


@task
def run(c, board, command, cwd=""):  # pragma: no cover
    "Run command remotely"

    bh = c.board(board)

    if not cwd:
        cwd = bh.model.rundir

    with bh.connect() as con:
        con.run("mkdir -p {}".format(str(cwd)))
        with con.cd(str(cwd)):
            con.run(command)


@task
def put(c, board, file, remote_path=""):  # pragma: no cover
    "Put file on the board"

    bh = c.board(board)
    with bh.connect() as con:
        if not remote_path:
            remote_path = bh.model.rundir
            remote_file = remote_path / Path(file).name

        else:
            remote_file_path = Path(remote_path)

        con.run("mkdir -p {}".format(str(remote_file.parent)))
        con.put(str(file), str(remote_file))


@task
def get(c, board, remote, local=""):  # pragma: no cover
    "get file from the board"

    bh = c.board(board)
    with bh.connect() as con:
        if local:
            local_path = Path(local)
            if local_path.is_dir():
                local_path.mkdir(parents=True, exist_ok=True)
            else:
                local_path.parent.mkdir(parents=True, exist_ok=True)

        con.get(remote=str(remote), local=str(local))

    raise Exception("Not Implemented")


@task
def lock(c, board):  # pragma: no cover
    board = c.board(board)
    board.lock()


@task
def unlock(c, board):  # pragma: no cover
    board = c.board(board)
    board.unlock()


@task
def reboot(c, board, wait=False):  # pragma: no cover
    """Reboots the board
       
       If -w / --wait is given waits untile the boards is reachable via ssh again
    """

    board = c.board(board)
    board.reboot(wait)


@task
def reset(c, board, wait=False):  # pragma: no cover
    """Does a hard reset of the board
    
       If -w / --wait is given waits until the board is reachable again
    """

    board = c.board(board)
    board.reset(wait)


@task
def install(c, board, package):  # pragma: no cover
    """Installs a package on the board"""

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
    """Starts a remote shell on the given board"""

    board = c.board(board)

    with board.connect() as con:
        con.run("$SHELL", pty=True)


@task
def board_ids(c, locked_ok=False):
    """returns list of board_ids suitable for usage in shell scripts"""
    for board in c.boards():
        if locked_ok or not board.is_locked():
            print(board.id)


@task
def get_kernel_config(c, board, target=""):
    board = c.board(board)
    if target:
        target = Path(target)

    with board.connect() as con:
        con.get("/proc/config.gz", str(target))


@task
def rsync_to(c, board, source, target="", delete=False):
    board = c.board(board)

    if not target:
        target = board.rundir

    with board.connect() as con:
        rsync(con, source=source, target=target, delete=delete)
