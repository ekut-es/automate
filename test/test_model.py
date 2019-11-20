from automate.loader import ModelLoader


def test_compiler_loader():
    loader = ModelLoader()
    models = loader.load_compilers()
    assert len(models) > 0
    print(models)


def test_board_loader():
    loader = ModelLoader()
    boards = loader.load_boards()

    assert len(boards) > 0
