import os
from pathlib import Path


def runtime_dir() -> Path:
    env_dir = os.getenv("XDG_RUNTIME_DIR")
    if env_dir is None:
        dir = Path("~/.automate").expanduser()
    else:
        dir = Path(env_dir)

    dir = dir / "automate"
    dir.mkdir(exist_ok=True, parents=True)

    return dir
