from invoke import task


@task
def say_hello(c):
    for board in c.boards():
        with board.connect() as con:
            con.run('echo "Hello from $(hostname)!"')


@task
def compiler_info(c, board="", toolchain=""):
    board = c.board(board)

    for compiler in board.compilers(toolchain=toolchain):
        print("compiler:", compiler.name)
        print("  CC =", compiler.cc)
        print("  CFLAGS = ", compiler.cflags)
        print("  CXX =", compiler.cxx)
        print("  CXXFLAGS =", compiler.cxxflags)
        print("  LDFLAGS =", compiler.ldflags)
        print("  LDLIBS = ", compiler.libs)
        print("")
