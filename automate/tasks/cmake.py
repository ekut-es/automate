from fabric import task


def _get_builder(c, board, *args, **kwargs):
    board = c.board(board)
    cc = board.compiler()
    builder = cc.builder("cmake", *args, **kwargs)

    return builder


@task
def configure(c, board, builddir="", srcdir="", prefix="", D=[]):
    builder = _get_builder(
        c, board, builddir=builddir, srcdir=srcdir, prefix=prefix
    )
    builder.configure(c, cmake_definitions=D)


@task
def build(c, board, builddir="", srcdir="", prefix=""):
    builder = _get_builder(
        c, board, builddir=builddir, srcdir=srcdir, prefix=prefix
    )
    builder.build(c)


@task
def install(c, board, builddir="", srcdir="", prefix=""):
    builder = _get_builder(
        c, board, builddir=builddir, srcdir=srcdir, prefix=prefix
    )
    builder.install(c)


@task
def clean(c, board, builddir="", srcdir="", prefix=""):
    builder = _get_builder(
        c, board, builddir=builddir, srcdir=srcdir, prefix=prefix
    )
    builder.clean(c)


@task
def deploy(c, board, builddir="", srcdir="", prefix=""):
    builder = _get_builder(
        c, board, builddir=builddir, srcdir=srcdir, prefix=prefix
    )
    builder.deploy(c)


__all__ = ["configure", "build", "clean", "install", "deploy"]
