#!/usr/bin/env python3

import sys

import coloredlogs
from invoke import Collection, Config, Program

from . import __version__ as self_version
from . import tasks
from .config import AutomateConfig
from .executor import AutomateExecutor


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

    def execute(self):
        if "logging" in self.config and "level" in self.config.logging:
            coloredlogs.install(level=self.config.logging.level)
        else:
            coloredlogs.install(level="DEBUG")

        res = super(AutoTool, self).execute()
        return res


program = AutoTool(
    version=self_version,
    namespace=tasks.collection,
    config_class=AutomateConfig,
    executor_class=AutomateExecutor,
)


program_run = AutoTool(
    version=self_version,
    config_class=AutomateConfig,
    executor_class=AutomateExecutor,
)
