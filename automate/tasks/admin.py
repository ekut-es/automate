from fabric import task, Connection
from paramiko.ssh_exception import AuthenticationException
from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.validation import Validator, ValidationError
import patchwork.files
import datetime

import logging
import getpass

from ..utils import cpuinfo
from ..model.common import ISA, UArch, Vendor
from ..model import (
    CoreModel,
    BoardModel,
    TripleModel,
    OSModel,
    ISAExtension,
    SSHConnectionModel,
)
from pathlib import Path


class ISAValidator(Validator):
    isa_set = set((k.value for k in ISA))

    def validate(self, document):
        text = document.text.strip()
        if text not in self.isa_set:
            raise ValidationError(
                message="{} is not a valid ISA", cursor_position=len(text)
            )


class UArchValidator(Validator):
    uarch_set = set((k.value for k in UArch))

    def validate(self, document):
        text = document.text.strip()
        if text not in self.uarch_set:
            raise ValidationError(
                message="{} is not a valid Microarchitecture",
                cursor_position=len(text),
            )


class VendorValidator(Validator):
    vendor_set = set((k.value for k in Vendor))

    def validate(self, document):
        text = document.text.strip()
        if text not in self.vendor_set:
            raise ValidationError(
                message="{} is not a valid CPU Vendor",
                cursor_position=len(text),
            )


@task
def add_board(c, user="", host=""):

    if host == "":
        host = prompt("Host: ")

    if user == "":
        user = prompt("Username: ", default="{}".format(getpass.getuser()))

    try:
        con = Connection(user=user, host=host)
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

        keyfile = prompt(
            "SSH Public key file: ",
            default=str(c["identity"]) + ".pub",
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

    board_name = prompt("board name: ", default=hostname)
    board_id = prompt("board_id: ", default=hostname)

    board_model = board_id
    board_model = prompt("board model: ", default=board_model)

    board_description = prompt("board description: ", default="")

    rundir = "/home/{}/run".format(user)
    board_rundirrundir = prompt("board rundir: ", default=rundir)

    cpus = cpuinfo.cpuinfo(con)
    cpu_models = []
    # TODO: this is quite repetitive if there are many cores ;)
    for cpu in cpus:
        print("cpu: ", cpu.id)

        description = prompt(
            "  description: ", validator=None, default=cpu.description
        )
        uarch = prompt(
            "  microarchitecture: ",
            default=cpu.uarch.value if cpu.uarch.value != UArch.UNKNOWN else "",
            validator=UArchValidator(),
            completer=FuzzyWordCompleter(words=[k.value for k in UArch]),
        )

        vendor = prompt(
            "  vendor: ",
            default=cpu.vendor.value,
            validator=VendorValidator(),
            completer=FuzzyWordCompleter(words=[k.value for k in Vendor]),
        )

        isa = prompt(
            "  isa: ",
            default=cpu.isa.value if cpu.isa != ISA.UNKNOWN else "",
            validator=ISAValidator(),
            completer=FuzzyWordCompleter([k.value for k in ISA]),
        )

        # TODO: Prompt for isa extensions
        assert ISAExtension.UNKNOWN not in cpu.extensions

        cpu_model = CoreModel(
            id=cpu.id,
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
    sysroot = prompt("  sysroot: ", default="$(boardroot)/$(board_id)/sysroot")
    rootfs = prompt(
        "  rootfs: ", default="$(boardroot)/$(board_id)/$(board_id).img"
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
        id=board_id,
        description=board_description,
        board=board_model,
        rundir=rundir,
        connections=[SSHConnectionModel(username=user, host=host)],
        cores=cpu_models,
        os=os_model,
        model_file=Path("metadata") / "boards" / board_id,
        model_file_mtime=datetime.datetime.now(),
    )

    print(board_model)
