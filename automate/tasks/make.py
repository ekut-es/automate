from pathlib import Path

from fabric import task


@task
def configure(c, board, builddir="", srcdir="", prefix=""):  # pragma: no cover

    board = c.board(board)
    cc = board.compiler()
    builder = board.builder("make", builddir=builddir)

    builder.configure(cc, srcdir=Path(srcdir), prefix=Path(prefix))


@task
def build(c, board, builddir=""):  # pragma: no cover
    board = c.board(board)
    builder = board.builder("make", builddir=builddir)

    builder.build()


@task
def install(c, board, builddir=""):  # pragma: no cover
    board = c.board(board)
    builder = board.builder("make", builddir=builddir)

    builder.install()


@task
def clean(c, board, builddir=""):  # pragma: no cover
    board = c.board(board)
    builder = board.builder("make", builddir=builddir)

    builder.clean()


@task
def deploy(c, board, builddir=""):  # pragma: no cover
    board = c.board(board)
    builder = board.builder("make", builddir=builddir)

    builder.deploy()


__all__ = ["configure", "build", "clean", "install", "deploy"]
