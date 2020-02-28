from enum import Enum, unique
from typing import Tuple, Union


class VersionString(str):
    """Implements a string that supports correct ordering for common version numbering schemes.

    For example:
        VersionString("10.0.0") > VersionString("9.0.0")

    This is a very simple comparison by splitting each version 
    at . characters and then filling each component by prepending
    zeros until a length of 8 is reached, before comparison.
   
    So in the example above the actual comparison would be:

    "00000010.00000000.00000000" > "00000009.00000000.00000000"
    """

    @classmethod
    def __get_validators__(cls):  # For pydantic
        yield cls.validate

    @classmethod
    def validate(cls, v):  # For Pydantic
        v = str(v)
        return cls(v)

    def _fill_str(self, s: str) -> str:
        filled = []
        for point in s.split("."):
            filled.append(point.zfill(8))
        filled_str = ".".join(filled)
        return filled_str

    def __lt__(self, other: str) -> bool:
        return self._fill_str(self) < self._fill_str(other)

    def __le__(self, other: str) -> bool:
        return self._fill_str(self) <= self._fill_str(other)

    def __eq__(self, other: object) -> bool:
        try:
            other = str(other)
        except:
            return False

        return self._fill_str(self) == self._fill_str(other)

    def __ne__(self, other: object) -> bool:
        return not (self == other)

    def __gt__(self, other: str) -> bool:

        return self._fill_str(self) > self._fill_str(other)

    def __ge__(self, other: str) -> bool:
        return self._fill_str(self) >= self._fill_str(other)


class Toolchain(Enum):
    GCC = "gcc"
    LLVM = "llvm"

    UNKNOWN = "unknown"


class ConnectionType(Enum):
    UART = "uart"
    SSH = "ssh"


class OS(Enum):
    LINUX = "linux"
    GENERIC = "generic"


class Machine(Enum):
    AARCH64 = "aarch64"
    AARCH32 = "arm"


class Environment(Enum):
    GNU = "gnu"
    GNUEABI = "gnueabi"
    GNUEABIHF = "gnueabihf"


class AcceleratorType(Enum):
    GPU = "gpu"
    CPU = "cpu"
    AI = "ai"
    FPGA = "fpga"
    UNKNOWN = "unknown"
