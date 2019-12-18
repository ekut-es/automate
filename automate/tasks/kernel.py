import logging
import tarfile
from pathlib import Path

import requests
from fabric import task


def _get_builder(c, board, *args, **kwargs):
    board = c.board(board)
    cc = board.compiler()
    builder = cc.builder("kernel", *args, **kwargs)

    return builder


@task
def configure(c, board, kernel_id, config_options=[]):
    builder = _get_builder(c, board)

    builder.configure(c, kernel_id, config_options)


@task
def build(c, board, kernel_id):
    builder = _get_builder(c, board)

    builder.build(c, kernel_id)


@task
def install(c, board, kernel_id):
    builder = _get_builder(c, board)

    builder.install(c)


@task
def clean(c, board, kernel_id):
    builder = _get_builder(c, board)

    builder.clean(c)


@task
def get_board_config(
    c,
    board,
    kernel_id="default",
    tarball_url="",
    force=False,
    config_name="config",
):
    board = c.board(board)

    if kernel_id in set((kernel.id for kernel in board.os.kernels)):
        if not force:
            raise Exception(
                f"Kernel config already exists use --force to overwrite"
            )

    kernel_config = (
        board.model.model_file.parent / "kernel" / f"{kernel_id}_config"
    )
    kernel_source_name = Path(tarball_url).name
    kernel_source_path = (
        Path(c.config.automate["boardroot"])
        / board.id
        / "kernel"
        / kernel_source_name
    )

    kernel_source_path.parent.mkdir(exist_ok=True)
    c.run("wget -c {} -o {}".format(str(tarball_url), str(kernel_source_path)))

    with board.connect() as con:
        result = con.run("cat /proc/cmdline", hide="out")
        cmdline = result.stdout.strip()

        logging.info(f"cmdline: {cmdline}")

        result = con.run("zcat /proc/config.gz", hide="out")
        config = result.stdout

        result = con.run("uname -r", hide="out")
        version = result.stdout.strip()

        logging.info(f"version: {version}")


__all__ = ["configure", "build", "clean", "install", "from_board"]
