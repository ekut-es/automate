from fabric import task

import logging
import random
import subprocess
import shlex
import time
import tempfile
import re
import patchwork

from pathlib import Path

from ..utils import fix_symlinks


@task
def safe_rootfs(c, board):
    "Safe rootfs image of board to board directory"
    m = c.metadata
    bh = m.get_board_handler(board)

    port = 12345

    image_name = Path(bh.model.os.rootfs)
    image_name.parent.mkdir(parents=True, exist_ok=True)

    print("Cloning rootfs to {}\n".format(image_name))
    with bh.lock():

        logging.info("Connecting to target")

        con = bh.connect()

        con.run("uptime")

        result = con.run(
            "echo 1 | sudo tee /proc/sys/kernel/sysrq", hide="out")
        if result.return_code != 0:
            raise Exception("Could not enable sysrq triggers")

        mount_result = con.run("mount", hide="out")
        if mount_result.return_code != 0:
            raise Exception("Could not get mountpoints")
        mount_output = mount_result.stdout
        mount_table_pattern = re.compile("(.*) on (.*) type (.*) \((.*)\)")
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

        try:
            with open(image_name.with_suffix(".tmp"), "wb") as image_file:
                logging.info("Starting listener")
                reader_cmd = "nc -l {}".format(port)
                reader = subprocess.Popen(
                    shlex.split(reader_cmd), stdout=image_file)

                result = con.run(
                    "echo u | sudo tee /proc/sysrq-trigger", hide="out")
                if result.return_code != 0:
                    raise Exception("Could not remount file systems read only")

                with con.forward_remote(port):
                    logging.info("Starting writer")
                    res = con.sudo("dd if={} | nc -N localhost {}".format(rootdevice,
                                                                          port))
                    print("Finished!\n")

                    result = reader.wait()
                    if result != 0:
                        raise Exception("Could not write image!")
        except BaseException as e:
            if image_name.with_suffix(".tmp").exists():
                c.run("rm {}".format(image_name.with_suffix(".tmp")))
            raise e
        finally:
            print("Rebooting target {}".format(board))
            #con.sudo("shutdown -r now")

        logging.info("Sparsifying saved image")
        c.run("fallocate -d {0}".format(image_name.with_suffix(tmp)))
        if image_name.exists():
            c.run("mv {0} {1}".format(
                image_name, image_name.with_suffix(".bak")))

        c.run("mv {0}.tmp {1}".format(
            image_name.with_suffix(".tmp"), image_name))

        return 0


@task
def build_sysroot(c, board):
    "Build a sysroot for the given board"
    m = c.metadata
    bh = m.get_board_handler(board)

    image_path = Path(bh.model.os.rootfs)
    if not image_path.exists:
        safe_rootfs(c, board)

    try:
        tmp_path = Path(tempfile.mkdtemp())
        logging.debug("Using mountpoint {}".format(tmp_path))

        c.run("sudo mount -l {} {}".format(str(image_path), str(tmp_path)))

        try:
            patchwork.transfers.rsync(c,
                                      source=str(tmp_path),
                                      target=str(bh.model.sysroot),
                                      delete=True)

            fix_symlinks(bh.model.sysroot)

        finally:
            c.run("sudo umount {}".format(tmp_path))

    finally:
        c.run("sudo rmdir {}".format(tmp_path))


@task
def run(c, board, command, cwd=""):
    "Run command remotely"

    m = c.metadata
    bh = m.get_board_handler(board)

    if not cwd:
        cwd = bh.model.rundir

    with bh.lock():
        with bh.connect() as con:
            con.run("mkdir -p {}".format(cwd))
            with con.cd(cwd):
                con.run(command)


@task
def sudo(c, board, command, cwd):
    "Run command remotely with root privileges"
    m = c.metadata
    bh = m.get_board_handler(board)

    if not cwd:
        cwd = bh.model.rundir

    with bh.lock():
        with bh.connect() as con:
            con.run("mkdir -p {}".format(cwd))
            with con.cd(cwd):
                con.sudo(command)


@task
def put(c, board, file, remote_path=""):
    "Put file on the board"

    m = c.metadata
    bh = m.get_board_handler(board)
    con = bh.connect()

    raise Exception("Not Implemented")


@task
def get(c, board, file, remote_path=""):
    "get file from the board"

    m = c.metadata
    bh = m.get_board_handler(board)
    con = bh.connect()

    raise Exception("Not Implemented")


@task
def rsync(c, board, local_path, remote_path=""):

    m = c.metadata
    bh = m.get_board_handler(board)
    con = bh.connect()

    raise Exception("Not Implemented")
