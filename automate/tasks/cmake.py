from pathlib import Path

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
    D=[],
):  # pragma: no cover
    """ 
    Configure a cmake project for the build
    
    # Arguments

       -b, --board=STRING: Board for the build. required argument 
       -s, --srcdir=STRING: Directory containing CMakeLists.txt usually top of source directory, required argument
      --builddir=STRING: Directory containing the built project (default: builds/<board_name>)
       --cflags=STRING: Extra flags for C-Compiler
       --flags=STRING: Extra base flags, used for all compilers and linking (for example -flto)
       --libs=STRING: Extra libraries to linke with the binaries
       --ldflags=STRING: Extra flags for linking. Linker is execute through compiler so for actual linker flags use -Wl,--linkerflag
       --compiler-name=STRING: Select a specific compiler 
       --prefix=STRING: Install prefix on the board (default: board.rundir/name of srcdir)
       --toolchain=STRING: Select a different toolchain type choices: llvm, gcc (default: gcc)
       --cxxflags=STRING: Extra flags for C++ compiliation
       --[no-]uarch:  Enable / Disable uarch specific optimizations if uarch is not supported by the compiler 
       --[no-]isa: Enable / Disable isa specific optimizations
       --[no-]sysroot: Enable / Disable linking with default sysroot 
       -D=STRING: Extra definitions for the CMAKE Build e.g. "-D 'ENABLE_OPENCL=ON'"
    
    """

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

    builder = board.builder("cmake", builddir=builddir)

    builder.configure(cc, srcdir=srcdir, prefix=prefix, cmake_definitions=D)


@task
def build(c, board, builddir=""):  # pragma: no cover
    """build a cmake project for the board
    
    -b STRING, --board=STRING: Target board
    --builddir=STRING: Builddirectory (default: builds/<board_name>)
    """

    board = c.board(board)
    builder = board.builder("cmake", builddir=builddir)

    builder.build(c)


@task
def install(c, board, builddir=""):  # pragma: no cover
    """install cmake project for deployment in <builddir>/install

    -b STRING, --board=STRING: Target board
    --builddir=STRING: Builddirectory (default: builds/<board_name>)
    """

    board = c.board(board)
    builder = board.builder("cmake", builddir=builddir)

    builder.install(c)


@task
def deploy(c, board, builddir=""):  # pragma: no cover
    """Deploy installed cmake project on board in configured prefix

    -b STRING, --board=STRING: Target board
    --builddir=STRING: Builddirectory (default: builds/<board_name>)
    """

    board = c.board(board)
    builder = board.builder("cmake", builddir=builddir)

    builder.deploy(c)


@task
def clean(c, board, builddir=""):  # pragma: no cover
    """Remove the build directory
    
    -b STRING, --board=STRING: Target board
    --builddir=STRING: Builddirectory (default: builds/<board_name>)
    """

    board = c.board(board)
    builder = board.builder("cmake", builddir=builddir)

    builder.clean(c)


__all__ = ["configure", "build", "clean", "install", "deploy"]
