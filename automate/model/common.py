from enum import Enum, unique


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
