from automate.utils import *
from automate.model import SSHConnectionModel, UARTConnectionModel

from pathlib import Path
import tempfile
import pytest


def test_connection_to_string():
    uart_model = UARTConnectionModel(device="/dev/ttyACM0")
    assert connection_to_string(uart_model) == "uart"

    ssh_model = SSHConnectionModel(username="test", host="test.test.com")
    assert connection_to_string(ssh_model) == "ssh"


def test_fix_symlinks():
    files = [
        "a.txt",
        "b.txt",
        "c.txt",
        "d.txt",
        "e.txt",
        "f.txt",
        "very_long_filename.txt",
        "file_in/subdirectory.txt",
    ]

    with tempfile.TemporaryDirectory() as tmp:
        links = []
        tmp_path = Path(tmp)
        tmp_len = len(tmp_path.parts)

        assert tmp_len >= 2

        for f_name in files:
            f_path = tmp_path / "files" / f_name
            link_path = tmp_path / "links" / f_name
            f_path.parent.mkdir(parents=True, exist_ok=True)
            link_path.parent.mkdir(parents=True, exist_ok=True)
            links.append(link_path)
            with f_path.open("w") as f:
                f.write(f_path.name)

            assert f_path.is_absolute()

            link_target = Path(f_path.parts[0], *f_path.parts[tmp_len:])
            link_path.symlink_to(link_target)

        for link_path in links:
            with pytest.raises(FileNotFoundError):
                link_path.resolve(strict=True)

        fix_symlinks(tmp_path)
        for link_path in links:
            resolved = link_path.resolve(strict=True)
            with resolved.open("r") as f:
                content = f.read()
                assert content.strip() == link_path.name
