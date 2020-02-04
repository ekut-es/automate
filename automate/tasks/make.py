from pathlib import Path

from fabric import task


@task
def configure(
    c,
    board,
    builddir="",
    srcdir="",
    prefix="",
    flags="",
    cflags="",
    cxxflags="",
    ldflags="",
    libs="",
    sysroot=True,
    isa=True,
    uarch=True,
):  # pragma: no cover

    board = c.board(board)
    cc = board.compiler()
    cc.configure(
        flags=flags,
        cflags=cflags,
        cxxflags=cxxflags,
        ldflagx=ldflags,
        uarch_opt=uarch,
        isa_opt=isa,
        enable_sysroot=sysroot,
        libs=libs,
    )
    builder = board.builder("make", builddir=builddir)

    builder.configure(cc, srcdir=srcdir, prefix=prefix)


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
