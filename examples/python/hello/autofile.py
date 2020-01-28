from invoke import task


@task()
def build(c, board_id):
    "Builds run cmake"

    board = c.board(board_id)
    builder = board.compiler().builder("make", srcdir="hello")
    builder.configure(c)
    builder.build(c)
    builder.install(c)
    builder.deploy(c)

    return True


@task()
def run(c, board_id):
    "Run the example on the given board"

    board = c.board(board_id)

    with board.connect() as con:
        with board.lock_ctx():
            with con.cd(str(board.rundir)):
                con.run("hello/hello")


@task()
def all(c):
    "Build example for all boards then execute on all boards"

    for board in c.boards():
        print(f"Build and Deploy for {board.id}")
        build(c, board.id)

    for board in c.boards():
        print(f"Run for {board.id}")
        run(c, board.id)