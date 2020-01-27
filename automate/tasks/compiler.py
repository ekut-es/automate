import logging
from pathlib import Path

from invoke import Collection, task


@task
def compile(
    c, board, files=[], output="a.out", compiler="", builddir=""
):  # pragma: no cover
    """Compiles multiple source files to a target specific executable

       Output will be placed in: build/{board_id} by default

       -b/--board: taget board
       -f/--files: source code files supports C/C++/Object Code files 
                   .cc, .cxx, .cpp, .C, .c++ are interpreted as C++
                   .o and .obj as Object Code (are only linked in)
                   the rest is given to the C Compiler  
    """

    logging.warning(
        "Using compile tasks to build binaries is probably not safe"
    )
    logging.warning("It might make sense to switch to one of the builders")

    board = c.board(board)
    compiler = board.compiler(compiler)

    logging.info(
        "Compiling {} with compiler {}".format(", ".join(files), compiler.id)
    )

    cc = compiler.bin_path / compiler.cc
    cxx = compiler.bin_path / compiler.cxx

    if not builddir:
        builddir = compiler.default_builddir

    build_path = Path(builddir)
    build_path.mkdir(exist_ok=True, parents=True)

    objs = []
    is_cpp = False

    # Compile
    for f in (Path(f) for f in files):
        if not f.exists():
            raise Exception("{} does not exist".format(f))

        if f.suffix == ".o":
            objs.append(f)
            continue

        obj = build_path / (f.stem + ".o")
        objs.append(obj)

        comp = cc
        flags = compiler.cflags
        if f.suffix in ["cc", "cxx", "cpp", "C", "c++"]:
            comp = cxx
            flags = cxxflags
            is_cpp = True

        cmd_list = [comp, "-c", "-o", obj, flags, f]
        cmd = " ".join((str(i) for i in cmd_list))
        logging.info("COMPILE: {}".format(cmd))
        c.run(cmd)

    # Link
    linker = cc
    if is_cpp:
        linker = cxx

    binary = build_path / output
    cmd_list = [linker, "-o", binary, compiler.ldflags] + objs
    cmd = " ".join((str(i) for i in cmd_list))
    logging.info("LINK: {}".format(cmd))
    c.run(cmd)
