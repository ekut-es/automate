import os
from collections import Counter

import pytest

from automate.config import AutomateConfig
from automate.loader import ModelLoader

root_path = os.path.dirname(os.path.abspath(__file__))
metadata_path = os.path.join(root_path, "src", "metadata")


def test_model_load():
    config = AutomateConfig()
    config["metadata"] = str(metadata_path)
    loader = ModelLoader(config)
    model = loader.load()

    assert len(model.boards) > 0
    assert len(model.compilers) > 0

    checked_boards = ["jetsontx2", "jetsonagx", "zynqberry"]
    for board in model.boards:
        checked_boards.remove(board.id)
    assert len(checked_boards) == 0

    c = Counter()
    for board in model.boards:
        c[board.id] += 1

    for key, val in c.items():
        assert val == 1
