from fabric import task

from ..model.common import Toolchain


@task
def configure(
    c,
    board,
    builddir="",
    srcdir="",
    prefix="",
    flags=None,
    cflags=None,
    cxxflags=None,
    ldflags=None,
    libs=None,
    sysroot=True,
    isa=True,
    uarch=True,
    toolchain="gcc",
    compiler_name="",
):  # pragma: no cover

    board = c.board(board)

    toolchain = Toolchain(toolchain) if toolchain else Toolchain.GCC

    cc = board.compiler(toolchain=toolchain, compiler_name=compiler_name)
    cc.configure(
        flags=flags,
        cflags=cflags,
        cxxflags=cxxflags,
        ldflags=ldflags,
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
