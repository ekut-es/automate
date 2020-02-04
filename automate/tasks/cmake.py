from pathlib import Path

from fabric import task


@task
def configure(
    c, board, builddir="", srcdir="", prefix="", D=[]
):  # pragma: no cover
    """ Configure a cmake project for the build
    """

    board = c.board(board)
    cc = board.compiler()
    builder = board.builder("cmake", builddir=builddir)

    builder.configure(cc, srcdir=srcdir, prefix=prefix, cmake_definitions=[])


@task
def build(c, board, builddir="", srcdir="", prefix=""):  # pragma: no cover
    """build a cmake project for the board"""

    board = c.board(board)
    builder = board.builder("cmake", builddir=builddir)

    builder.build(c)


@task
def install(c, board, builddir="", srcdir="", prefix=""):  # pragma: no cover
    """install cmake project for deployment"""

    board = c.board(board)
    builder = board.builder("cmake", builddir=builddir)

    builder.install(c)


@task
def deploy(c, board, builddir="", srcdir="", prefix=""):  # pragma: no cover
    """Deploy installed cmake project on board"""

    board = c.board(board)
    builder = board.builder("cmake", builddir=builddir)

    builder.deploy(c)


@task
def clean(c, board, builddir="", srcdir="", prefix=""):  # pragma: no cover
    """Remove the build directory"""

    board = c.board(board)
    builder = board.builder("cmake", builddir=builddir)

    builder.clean(c)


__all__ = ["configure", "build", "clean", "install", "deploy"]
