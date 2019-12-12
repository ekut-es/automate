from fabric import task


def _get_builder(c, board, *args, **kwargs):
    board = c.board(board)
    cc = board.compiler()
    builder = cc.builder("kernel", *args, **kwargs)


@task
def configure(c, board):
    builder = _get_builder(c, board)


@task
def build(c, board):
    builder = _get_builder(c, board)


@task
def install(c, board):
    builder = _get_builder(c, board)


@task
def clean(c, board):
    builder = _get_builder(c, board)


__all__ = ["configure", "build", "clean", "install"]
