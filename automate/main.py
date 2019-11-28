#!/usr/bin/env python3

import sys

from invoke import Argument, Collection, Program


from invoke import __version__ as invoke_version
from paramiko import __version__ as paramiko_version
from fabric import __version__ as fabric_version
#from .import __version__ as self_version

from .import tasks


class AutoTool(Program):
    def print_version(self):
        #        print("automate: {}".format(self_version))
        print("fabric: {}".format(fabric_version))
        print("invoke: {}".format(invoke_version))
        print("paramiko: {}".format(paramiko_version))


program = AutoTool(name="automate")
#                   namespace=Collection.from_module(automate.tasks))
