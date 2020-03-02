import logging
import os
import tarfile
from pathlib import Path
from typing import List, Union

from ..model.board import SSHConnectionModel, UARTConnectionModel


def connection_to_string(
    connection: Union[SSHConnectionModel, UARTConnectionModel]
) -> str:
    table = {SSHConnectionModel: "ssh", UARTConnectionModel: "uart"}

    name = "UNKNOWN"

    t = type(connection)

    if t in table:
        name = table[t]

    return name


def fix_symlinks(base_path: Path) -> None:
    """ This function tries to fix symlinks in cloned buildroots by:

1. Searching for all symlinks with absolute target path in base_path
2. Prepending base_path to the target path
3. Making the targets of the links relative to the symlink location
4. Deleting the symlink and replacing it with one to the relative location
 """

    logging.info("Changing absolute symlinks to relative symlinks")
    links: List[str] = []
    for root, _, files in os.walk(base_path):
        for filename in files:
            path = os.path.join(root, filename)
            if os.path.islink(path):
                links.append(path)
            else:
                # If it's not a symlink we're not interested.
                continue

    for link in links:
        target = os.readlink(link)
        if os.path.isabs(target):
            new_target = str(base_path) + str(target)
            new_target_rel = os.path.relpath(
                new_target, os.path.dirname(os.path.abspath(link))
            )

            logging.debug(
                "Relinking\n  link: {}\n  target: {}\n  new_target: {}\n  new_target_rel: {}\n  base_path: {}".format(
                    link, target, new_target, new_target_rel, base_path
                )
            )

            os.unlink(link)
            os.symlink(new_target_rel, link)


def untar(
    tar_path: Union[str, Path], extract_path: Union[str, Path] = "."
) -> None:
    tar_path = Path(tar_path)
    extract_path = Path(extract_path)

    if not extract_path.exists():
        extract_path.mkdir(parents=True)

    with tarfile.open(name=tar_path, mode="r|*") as tar_file:
        tar_file.extractall(extract_path)
