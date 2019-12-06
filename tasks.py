from invoke import task


@task
def black(c):
    "Runs black code formatter"
    c.run("black --py36 -l 80 .")


@task
def mypy(c):
    "Run static typechecker on the code"
    c.run("mypy automate")


@task
def test(c):
    "Run test suite"
    c.run("pytest --cov automate test --cov-config=pyproject.toml")


@task(test)
def cov(c):
    "Generate html coverage report"
    c.run("coverage html")
    c.run("xdg-open htmlcov/index.html")


@task
def monkeytype(c):
    "Run testsuite and collect dynamic type information"
    c.run("pytest --monkeytype-output=monkeytype.sqlite3 test")


@task
def pre_commit(c):
    "Installs pre commit hooks"
    c.run("pre-commit install")
