#!/usr/bin/env python3

import sys

from invoke import Program, Collection, Config
from .config import AutomateConfig
from .executor import AutomateExecutor

from . import __version__ as self_version
from . import tasks


class AutoTool(Program):
    def core_args(self):
        core_args = super(AutoTool, self).core_args()

        return core_args

    def print_version(self):
        from invoke import __version__ as invoke_version
        from paramiko import __version__ as paramiko_version
        from fabric import __version__ as fabric_version

        print("version: {}".format(self_version))
        print("  fabric: {}".format(fabric_version))
        print("  invoke: {}".format(invoke_version))
        print("  paramiko: {}".format(paramiko_version))


program = AutoTool(
    version=self_version,
    config_class=AutomateConfig,
    namespace=tasks.collection,
    executor_class=AutomateExecutor,
)
