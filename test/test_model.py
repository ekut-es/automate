import pytest
from collections import Counter

from automate.loader import ModelLoader


def test_model_load():
    loader = ModelLoader()
    model = loader.load_model()

    assert len(model.boards) > 0
    assert len(model.compiler) > 0

    with pytest.raises(TypeError):
        model.compiler[0].name = "test"

    checked_boards = ["jetsontx2", "jetsonagx"]
    for board in model.boards:
        checked_boards.remove(board.id)
    assert len(checked_boards) == 0

    c = Counter()
    for board in model.boards:
        c[board.id] += 1

    for key, val in c.items():
        assert val == 1
