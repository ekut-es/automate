from invoke import task


@task
def list(c, boards=True, compilers=True):
    c.run('echo "Hello World!"')
