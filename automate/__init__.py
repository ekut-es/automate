from .config import configure

__version_info__ = (0, 0, 1)
__version__ = ".".join(map(str, __version_info__))

__all__ = ["configure", "__version_info__", "__version__"]
