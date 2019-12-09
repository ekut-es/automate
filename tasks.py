from invoke import task


@task
def black(c):
    "Runs black code formatter"
    c.run("black --py36 -l 80 automate test")


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


@task
def update_schemas(c):
    from automate.model import CompilerModel, BoardModel
    from pathlib import Path

    board_json = BoardModel.schema_json(indent=2)
    compiler_json = CompilerModel.schema_json(indent=2)

    path = Path("docs/schema")
    path.mkdir(exist_ok=True)

    with (path / "board.json").open("w") as f:
        f.write(board_json)

    with (path / "compiler.json").open("w") as f:
        f.write(compiler_json)


@task
def doc(c):
    "Starts the documentation viewer"

    c.run("mkdocs serve")
