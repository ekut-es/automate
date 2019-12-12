import os
import sys
from pathlib import Path

from invoke import task


@task
def isort(c):
    root_path = Path(os.path.dirname(os.path.abspath(__file__)))
    with c.cd(str(root_path)):
        c.run("isort automate test")


@task(isort)
def black(c):
    "Runs black code formatter"
    root_path = Path(os.path.dirname(os.path.abspath(__file__)))
    with c.cd(str(root_path)):
        c.run("black --py36 -l 80 automate test")


@task
def mypy(c):
    "Run static typechecker on the code"
    root_path = Path(os.path.dirname(os.path.abspath(__file__)))
    with c.cd(str(root_path)):
        c.run("mypy automate")


@task
def test(c):
    "Run test suite"
    root_path = Path(os.path.dirname(os.path.abspath(__file__)))
    with c.cd(str(root_path)):
        c.run("pytest --cov automate test --cov-config=pyproject.toml")


@task(test)
def cov(c):
    "Generate html coverage report"
    root_path = Path(os.path.dirname(os.path.abspath(__file__)))
    with c.cd(str(root_path)):
        c.run("coverage html")
        c.run("xdg-open htmlcov/index.html")


@task
def monkeytype(c):
    "Run testsuite and collect dynamic type information"
    root_path = Path(os.path.dirname(os.path.abspath(__file__)))
    with c.cd(str(root_path)):
        c.run("pytest --monkeytype-output=monkeytype.sqlite3 test")


@task
def pre_commit(c):
    "Installs pre commit hooks"
    root_path = Path(os.path.dirname(os.path.abspath(__file__)))
    with c.cd(str(root_path)):
        c.run("pre-commit install")


@task
def update_schemas(c):
    from automate.model import CompilerModel, BoardModel, MetadataModel

    root_path = Path(os.path.dirname(os.path.abspath(__file__)))

    metadata_json = MetadataModel.schema_json(indent=2)
    # board_json = BoardModel.schema_json(indent=2,by_alias=True)
    # compiler_json = CompilerModel.schema_json(indent=2, by_alias=True)

    path = root_path / "docs" / "schema"
    path.mkdir(exist_ok=True)

    with (path / "metadata.schema.json").open("w") as f:
        f.write(metadata_json)

    # with (path / "board.schema.json").open("w") as f:
    #    f.write(board_json)

    # with (path / "compiler.schema.json").open("w") as f:
    #    f.write(compiler_json)

    tmp_path = root_path / "tmp"
    tmp_path.mkdir(exist_ok=True)

    with c.cd(str(tmp_path)):
        node_path = tmp_path / "node-v12.13.1-linux-x64"
        if not node_path.exists():
            c.run(
                "wget https://nodejs.org/dist/v12.13.1/node-v12.13.1-linux-x64.tar.xz"
            )
            c.run("tar xvJf node-v12.13.1-linux-x64.tar.xz")
        os.environ["PATH"] = str(node_path / "bin") + ":" + os.environ["PATH"]
        c.run("npm install -g @adobe/jsonschema2md")
        c.run("jsonschema2md -d {0} -o {0}".format(path))


@task
def doc(c):
    "Starts the documentation viewer"

    root_path = Path(os.path.dirname(os.path.abspath(__file__)))
    with c.cd(str(root_path)):
        c.run("mkdocs serve")


@task
def fake_board(c, clean=False):
    "Runs a fake board for integration tests"

    root_path = os.path.dirname(os.path.abspath(__file__))
    fake_board_path = os.path.join(root_path, "test/fake_board_data")
    build_path = os.path.join(root_path, "tmp/fakechroot")

    if clean:
        c.run("rm -rf {0}".format(build_path))

    c.run("mkdir -p {0}".format(build_path))

    with c.cd(build_path):
        if not os.path.exists(os.path.join(c.cwd, "fakechroot-2.20.1")):
            c.run(
                "wget https://github.com/dex4er/fakechroot/releases/download/2.20.1/fakechroot-2.20.1.tar.gz"
            )
            c.run("tar xvzf fakechroot-2.20.1.tar.gz")
        with c.cd("fakechroot-2.20.1"):
            if not os.path.exists(os.path.join(c.cwd, "configure")):
                c.run("./autogen")

            if not os.path.exists(os.path.join(c.cwd, "Makefile")):
                c.run(
                    "./configure --prefix={0}/fakechroot".format(
                        fake_board_path
                    )
                )

            c.run("make")
            c.run("make install")
