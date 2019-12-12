from collections import Counter

import pytest

from automate.config import AutomateConfig
from automate.loader import ModelLoader


def test_model_load():
    config = AutomateConfig()
    loader = ModelLoader(config)
    model = loader.load()

    assert len(model.boards) > 0
    assert len(model.compilers) > 0

    checked_boards = ["jetsontx2", "jetsonagx"]
    for board in model.boards:
        checked_boards.remove(board.id)
    assert len(checked_boards) == 0

    c = Counter()
    for board in model.boards:
        c[board.id] += 1

    for key, val in c.items():
        assert val == 1
