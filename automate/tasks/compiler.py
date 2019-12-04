from invoke import task, Collection
import logging
from pathlib import Path


@task
def compile(c, board, files=[], output="a.out", compiler="", builddir=""):
    """Compiles multiple source files to a target specific executable

       Output will be placed in: build-{board_id} by default
    """

    generator = CrossCompilerGenerator(c.metadata)

    board = c.board(board)
    compiler = c.compiler(compiler)

    logging.info(
        "Compiling {} with compiler {}".format(", ".join(files), compiler.id)
    )

    cc = compiler.bin_path / compiler.cc
    cxx = compiler.bin_path / compiler.cxx

    if not builddir:
        builddir = "build-{}".format(board)

    build_path = Path(builddir)
    build_path.mkdir(exist_ok=True)

    objs = []
    is_cpp = False
    # Compile
    for f in (Path(f) for f in files):
        if not f.exists():
            raise Exception("{} does not exist".format(f))

        obj = build_path / (f.stem + ".o")
        objs.append(obj)

        comp = cc
        if f.suffix in ["cc", "cxx", "cpp", "C", "c++"]:
            comp = cxx
            is_cpp = True

        cmd_list = [comp, "-c", "-o", obj, compiler.cflags, f]
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
