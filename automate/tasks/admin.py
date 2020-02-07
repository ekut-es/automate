import concurrent
import datetime
import getpass
import logging
import os.path
import re
import shlex
import shutil
import subprocess
import tempfile
from collections import namedtuple
from enum import Enum
from pathlib import Path

import patchwork.files
from fabric import Connection, task
from paramiko.ssh_exception import AuthenticationException
from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.validation import ValidationError, Validator
from ruamel.yaml import YAML  # type: ignore

from ..loader import ModelLoader
from ..model import (
    BoardModel,
    CoreModel,
    OSModel,
    SSHConnectionModel,
    TripleModel,
)
from ..utils import cpuinfo, fix_symlinks
from ..utils.network import find_local_port


@task
def add_users(c):  # pragma: no cover
    """Add user ssh keys to all boards
    """
    loader = ModelLoader(c.config)
    users = loader.load_users()

    def copy_keys(sftp, users, homedir):
        patchwork.files.directory(con, "~/.ssh", mode="700")

        authorized_keys = homedir / ".ssh" / "authorized_keys"
        with sftp.open(str(authorized_keys), "w") as authorized_keys_file:
            for user_id, user in users.users.items():
                authorized_keys_file.write("# {}\n".format(user_id))
                for ssh_key in user.public_keys:
                    ssh_key = ssh_key.strip()
                    authorized_keys_file.write("{}\n".format(ssh_key))

    FrozenGateway = namedtuple("FrozenGateway", ["host", "username", "port"])

    gateways = set()

    for board in c.boards():
        if board.gateway is not None:
            gateways.add(FrozenGateway(**board.gateway.dict()))

        with board.connect() as con:

            sftp = con.sftp()
            homedir = board.homedir()

            copy_keys(sftp, users, homedir)

    for gw in gateways:
        identity = os.path.expanduser(c.config.automate.identity)
        with Connection(
            host=gw.host,
            user=gw.username,
            port=gw.port,
            connect_kwargs={"key_filename": identity},
        ) as con:

            result = con.run("echo $HOME", hide=True)
            gw_homedir = Path(result.stdout.strip())
            sftp = con.sftp()
            copy_keys(sftp, users, gw_homedir)


@task
def safe_rootfs(c, board):  # pragma: no cover
    """Safe rootfs image of board
       
        -b/--board: target board name
    """
    bh = c.board(board)

    port = find_local_port()

    image_name = Path(bh.os.rootfs)
    image_name.parent.mkdir(parents=True, exist_ok=True)

    print("Cloning rootfs to {}\n".format(image_name))

    with bh.lock_ctx():

        logging.info("Connecting to target using port {}".format(port))

        con = bh.connect()

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

                        shutil.copyfileobj(reader.stdout, image_file)
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
                            "sudo dd if={} |  nc -N localhost {}".format(
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

        logging.info("Backup existing image")
        if image_name.exists():
            c.run(
                "mv {0} {1}".format(image_name, image_name.with_suffix(".bak"))
            )

        logging.info("Fsck image")
        c.run("fsck -p {}".format(image_name.with_suffix(".tmp")))

        logging.info("Moving image to result")
        c.run("mv {0} {1}".format(image_name.with_suffix(".tmp"), image_name))
        print("Finished image saving.")

        return 0


@task
def build_sysroot(c, board):  # pragma: no cover
    """Build compiler sysroot for board
       
        -b/--board: target board id
    """

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






board_yaml_template = r"""
name: 
hostname: 
board: 
description: 
rundir:

# Links to documentation of these boards
doc:

# Gateway used for this board
gateway:
  host:
  username:

# Available UART and SSH Connections
connections:
  - 
    host:
    username:

# Available Cores
cores:
  -
    id:
    description: 
    isa:
    uarch: 
    vendor: 

# Description of the Board OS and the available kernels
os:
  triple:
    os: 
    machine: 
    environment:
    distribution:
    release: 
    description: 
    sysroot:
    rootfs: 
    multiarch: 
    kernels: 
      - 
        id: 
        description: 
        version: 
        commandline: 
        kernel_srcdir: 
        kernel_config: 
        kernel_source: 
        default:
"""


@task
def add_board(c, user="", host="", port=22):  # pragma: no cover
    # TODO: add configuration of gateway

    if host == "":
        host = prompt("Host: ")

    if user == "":
        user = prompt("Username: ", default="{}".format(getpass.getuser()))

    try:
        con = Connection(user=user, host=host, port=port)
        con.open()
    except AuthenticationException as e:
        print("Could not Authenticate with public key")
        password = prompt(
            "Password for {}@{}: ".format(user, host), is_password=True
        )
        con = Connection(
            user=user, host=host, connect_kwargs={"password": password}
        )
        con.open()

        identity = os.path.expanduser(c.config.automate.identity)
        keyfile = prompt(
            "SSH Public key file: ",
            default=str(identity) + ".pub",
            is_password=False,
        )

        with open(keyfile) as f:
            key = f.read()

            patchwork.files.directory(con, "~/.ssh", mode="700")
            patchwork.files.append(con, "~/.ssh/authorized_keys", key)

            con.close()

            con = Connection(user=user, host=host)
            con.open()

    assert con.is_connected

    result = con.run("hostname", hide="stdout", warn=True)
    hostname = ""
    if result.return_code == 0:
        hostname = result.stdout.strip()

    board_name = prompt("board_name: ", default=hostname)
    model_file = (
        Path(c.config.automate.metadata)
        / "boards"
        / board_name
        / "description.yml"
    )
    if model_file.exists():
        logging.error("board with id {0} already exists".format(board_name))
        return -1


    board_model = board_name
    board_model = prompt("board model: ", default=board_model)

    board_description = prompt("board description: ", default="")

    rundir = "/home/{}/run".format(user)
    board_rundirrundir = prompt("board rundir: ", default=rundir)

    cpus = cpuinfo.cpuinfo(con)
    cpu_models = []
    # TODO: this is quite repetitive if there are many cores ;)
    for cpu in cpus:
        print("cpu: ", cpu.num)

        description = prompt(
            "  description: ", validator=None, default=cpu.description
        )
        uarch = prompt(
            "  microarchitecture: ",
            default=cpu.uarch,
        )

        vendor = prompt(
            "  vendor: ",
            default=cpu.vendor,
        )

        isa = prompt(
            "  isa: ",
            default=cpu.isa,
        )

        # TODO: Prompt for isa extensions
        
        cpu_model = CoreModel(
            id=cpu.num,
            isa=isa,
            uarch=uarch,
            vendor=vendor,
            extensions=cpu.extensions,
            description=description,
        )
        cpu_models.append(cpu_model)

    print("OS Configuration")
    # TODO: get default triple
    # TODO: Add validator

    t_machine = "arm64"
    result = con.run("uname --machine", hide="stdout", warn=True)
    if result.return_code == 0:
        t_machine = result.stdout.strip()

    machine_sentinels = {
        "armv7l": "arm",
        "arm": "arm",
        "aarch64": "aarch64",
        "arm64": "aarch64",
    }

    if t_machine in machine_sentinels:
        t_machine = machine_sentinels[t_machine]

    t_abi = "gnueabihf"
    if t_machine == "aarch64":
        t_abi = "gnu"

    triple = prompt(
        "  triple (machine-vendor-os-vendor): ",
        default="{}-unknown-linux-{}".format(t_machine, t_abi),
    )
    t_machine, t_vendor, t_os, t_abi = triple.split("-")
    triple = TripleModel(
        machine=t_machine, vendor=t_vendor, os=t_os, environment=t_abi
    )

    result = con.run("cat /etc/os-release", hide="stdout", warn=True)
    distribution = ""
    release = ""
    if result.return_code == 0:
        for line in result.stdout.split("\n"):
            line = line.strip()
            if len(line.split("=")) != 2:
                continue
            k, v = line.split("=")
            v = v.strip('"')

            if k == "ID":
                distribution = v
            elif k == "VERSION_ID":
                version = v

    distribution = prompt("  distribution: ", default=distribution)
    version = prompt("  version: ", default=version)
    description = ""
    sysroot = prompt("  sysroot: ", default="${boardroot}/${board_name}/sysroot")
    rootfs = prompt(
        "  rootfs: ", default="${boardroot}/${board_name}/${board_name}.img"
    )
    multiarch = False
    if distribution in ["ubuntu", "debian"]:
        multiarch = True

    # TODO: extract kernel info
    os_model = OSModel(
        triple=triple,
        distribution=distribution,
        release=release,
        description=description,
        sysroot=sysroot,
        rootfs=rootfs,
        multiarch=multiarch,
    )

    board_model = BoardModel(
        name=board_name,
        description=board_description,
        board=board_model,
        rundir=rundir,
        connections=[SSHConnectionModel(username=user, host=host, port=port)],
        cores=cpu_models,
        os=os_model,
        model_file=model_file,
        model_file_mtime=datetime.datetime.now(),
    )

    model_file.parent.mkdir(parents=True, exist_ok=True)

    yaml = YAML(typ="rt")
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)

    yaml.load(board_yaml_template)
    with model_file.open("w") as mf:
        d = board_model.dict(exclude={"model_file", "model_file_mtime"})

        def _recurse(d):
            if isinstance(d, dict):
                for k, v in d.items():
                    d[k] = _recurse(v)
                return d
            elif isinstance(d, list):
                return [_recurse(item) for item in d]
            elif isinstance(d, Enum):
                return d.value
            elif isinstance(d, Path):
                return str(d)
            else:
                return d

        d = _recurse(d)
        yaml.dump(d, mf)
