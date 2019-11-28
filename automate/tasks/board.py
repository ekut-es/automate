from fabric import task


@task
def run(c, board, command):
    "Run command remotely"

    print("Run")
