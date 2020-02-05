import logging
import os
from collections import Counter

import pytest

from automate.config import AutomateConfig
from automate.loader import ModelLoader

root_path = os.path.dirname(os.path.abspath(__file__))
metadata_path = os.path.join(root_path, "src", "metadata")


def test_model_load():
    config = AutomateConfig()
    config.automate.metadata = str(metadata_path)

    loader = ModelLoader(config)
    model = loader.load()

    assert len(model.boards) > 0
    assert len(model.compilers) > 0

    checked_boards = ["jetsontx2", "jetsonagx", "zynqberry", "raspberrypi4b-jh1"]
    for board in model.boards:
        checked_boards.remove(board.name)
    assert len(checked_boards) == 0

    c = Counter()
    for board in model.boards:
        c[board.name] += 1

    for key, val in c.items():
        assert val == 1


def test_model_load_unexpanded():

    config = AutomateConfig()
    config.automate.metadata = str(metadata_path)
    loader = ModelLoader(config)
    model = loader.load(expand_templates=False)
    for board in model.boards:
        assert str(board.os.sysroot).startswith("${boardroot}")


def test_model_load_users():
    config = AutomateConfig()
    config.automate.metadata = str(metadata_path)
    loader = ModelLoader(config)

    users = loader.load_users()
    assert len(users.users) > 0
    assert "gerum" in users.users
