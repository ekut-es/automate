import pytest

from automate.loader import ModelLoader


def test_model_load():
    loader = ModelLoader()
    model = loader.load_model()

    assert len(model.boards) > 0
    assert len(model.compiler) > 0

    with pytest.raises(TypeError):
        model.compiler[0].name = "test"
