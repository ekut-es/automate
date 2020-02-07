import logging
import tarfile
from pathlib import Path

import requests
from fabric import task

from ..model.common import Toolchain


def _get_builder(c, board, builddir):  # pragma: no cover
    board = c.board(board)
    builder = board.builder("kernel", builddir=builddir)

    return builder


@task
def configure(
    c,
    board,
    kernel_id,
    builddir="",
    flags="",
    cflags="",
    cxxflags="",
    ldflags="",
    libs="",
    sysroot=True,
    isa=True,
    uarch=True,
    toolchain="gcc",
    compiler_id="",
):  # pragma: no cover
    builder = _get_builder(c, board, builddir)
    board = builder.board

    toolchain = Toolchain(toolchain) if toolchain else Toolchain.GCC

    cc = board.compiler(toolchain=toolchain, compiler_id=compiler_id)
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

    builder.configure(kernel_id, cc)


@task
def build(c, board, builddir=""):  # pragma: no cover
    builder = _get_builder(c, board, builddir)

    builder.build()


@task
def install(c, board, builddir=""):  # pragma: no cover
    builder = _get_builder(c, board, builddir)

    builder.install()


@task
def clean(c, board, builddir=""):  # pragma: no cover
    builder = _get_builder(c, board, builddir)

    builder.clean()


__all__ = ["configure", "build", "clean", "install"]
