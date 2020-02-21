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
    """
       Configure a kernel project for the build
    
    # Arguments

       -b, --board=STRING: Board for the build. required argument 
       -k, --kernel-id=STRING: Name of the kernel configuration to build
      --builddir=STRING: Directory containing the built project (default: builds/<board_name>)
       --compiler-name=STRING: Select a specific compiler 
       --toolchain=STRING: Select a different toolchain type choices: llvm, gcc (default: gcc)
       
       Other arguments are ignored at the moment
    """
    builder = _get_builder(c, board, builddir)
    board = builder.board

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

    builder.configure(kernel_id, cc)


@task
def build(c, board, builddir=""):  # pragma: no cover
    """
    Build the project

    -b STRING, --board=STRING: Target board
    --builddir=STRING: Builddirectory (default: builds/<board_name>)
    """
    builder = _get_builder(c, board, builddir)

    builder.build()


@task
def install(c, board, builddir=""):  # pragma: no cover
    """
    Install the project in local directory <builddir>/<install>
 
    -b STRING, --board=STRING: Target board
    --builddir=STRING: Builddirectory (default: builds/<board_name>)
    """
    builder = _get_builder(c, board, builddir)

    builder.install()


@task
def clean(c, board, builddir=""):  # pragma: no cover
    """Remove build directory

    -b STRING, --board=STRING: Target board
    --builddir=STRING: Builddirectory (default: builds/<board_name>)
    """

    builder = _get_builder(c, board, builddir)

    builder.clean()


__all__ = ["configure", "build", "clean", "install"]
