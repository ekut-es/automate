from fabric import task


def _get_builder(c, board, *args, **kwargs):
    board = c.board(board)
    cc = board.compiler()
    builder = cc.builder("kernel", *args, **kwargs)

    return builder


@task
def configure(c, board, kernel_id):
    builder = _get_builder(c, board)

    builder.configure(c, kernel_id)


@task
def build(c, board, kernel_id):
    builder = _get_builder(c, board)

    builder.build(c, kernel_id)


@task
def install(c, board, kernel_id):
    builder = _get_builder(c, board)

    builder.install(c)


@task
def clean(c, board, kernel_id):
    builder = _get_builder(c, board)

    builder.clean(c)


__all__ = ["configure", "build", "clean", "install"]
