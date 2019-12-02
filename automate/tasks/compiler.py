from invoke import task, Collection
import logging
from pathlib import Path

from ..compiler import CrossCompilerGenerator


@task
def compile(c, board, files=[], compiler="", builddir=""):
    """Compiles multiple source files to a target specific executable

       Output will be placed in: build-{board_id} by default
    """

    generator = CrossCompilerGenerator(c.metadata)
    compiler = None
    if compiler:
        compiler = generator.get_compiler(compiler, board)
    else:
        compiler = generator.get_default_compiler(board)

    logging.info("Compiling {} with compiler {}".format(
        ", ".join(files), compiler.id))

    cc = compiler.bin_path / compiler.cc
    cxx = compiler.bin_path / compiler.cxx

    if not builddir:
        builddir = "build-{}".format(board)

    build_path = Path(builddir)
    build_path.mkdir(exist_ok=True)

    objs = []
    # Compile
    for f in (Path(f) for f in files):
        if not f.exists():
            raise Exception("{} does not exist".format(f))

        output = build_path / (f.stem + ".o")
        objs.append(output)

        comp = cc
        if f.suffix in ["cc", "cxx", "cpp", "C", "c++"]:
            comp = cxx

        cmd_list = [comp, "-c", "-o", output, compiler.cflags, f]
        cmd = " ".join((str(i) for i in cmd_list))
        logging.info("COMPILE: {}".format(cmd))
        c.run(cmd)

    # Link
