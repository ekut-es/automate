#!/usr/bin/env python3

import sys

from invoke import Program, Collection
from invoke.config import merge_dicts
from fabric import Config

from .import __version__ as self_version


from .import tasks
from .loader import get_model


class AutomateConfig(Config):
    prefix = 'automate'
    env_prefix = 'AUTOMATE'

    @staticmethod
    def global_defaults():
        their_defaults = Config.global_defaults()
        metadata = get_model()

        my_defaults = {
            'metadata': metadata
        }

        return merge_dicts(their_defaults, my_defaults)


class AutoTool(Program):
    def print_version(self):
        from invoke import __version__ as invoke_version
        from paramiko import __version__ as paramiko_version
        from fabric import __version__ as fabric_version

        print("version: {}".format(self_version))
        print("  fabric: {}".format(fabric_version))
        print("  invoke: {}".format(invoke_version))
        print("  paramiko: {}".format(paramiko_version))
        print("  pydantic: {}".format(pydantic_version))


program = AutoTool(version=self_version,
                   config_class=AutomateConfig,
                   namespace=Collection.from_module(tasks))
