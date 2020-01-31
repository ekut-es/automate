from invoke import task

from automate.model.common import Toolchain


def builds(c):
    "Builds run cmake"

    flags = ["-O0", "-O1", "-O2", "-O3"]

    for board in c.boards():
        for compiler in board.compilers():
            for flag in flags:
                print(
                    f"Building for {board.id} with {compiler.id} and flags {flag}"
                )
                cross_compiler = board.compiler(compiler.id)
                cross_compiler._flags = [flag]
                builddir = f"builds/{board.id}/{compiler.id}_{flag[1:]}"
                builder = board.builder("make", builddir=builddir)

                builder.configure(
                    cross_compiler=cross_compiler, srcdir="hello_compilers"
                )
                builder.build()

                yield builder


@task()
def run(c):
    for builder in builds(c):
        with builder.board.lock_ctx():
            builder.deploy(c)
            with builder.board.connect() as con:
                con.run(f"{builder.board.rundir}/hello_compilers/hello")
