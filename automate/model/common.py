from enum import Enum, unique


class Toolchain(Enum):
    GCC = "gcc"
    LLVM = "llvm"


class ISAExtension(Enum):
    AES = "aes"
    ASIMD = "asimd"
    CRC32 = "crc32"
    EDSP = "edsp"
    EVTSTRM = "evtstrm"
    FASTMULT = "fastmult"
    FP = "fp"
    HALF = "half"
    NEON = "neon"
    PMULL = "pmull"
    SHA1 = "sha1"
    SHA2 = "sha2"
    THUMB = "thumb"
    TLS = "tls"
    VFP = "vfp"
    VFPD32 = "vfpd32"
    VFPV3 = "vfpv3"
    UNKNOWN = "unknown"


class ISA(Enum):
    ARMV2 = "armv2"
    ARMV2A = "armv2a"
    ARMV3 = "armv3"
    ARMV3M = "armv3m"
    ARMV4 = "armv4"
    ARMV4T = "armv4t"
    ARMV5 = "armv5"
    ARMV5T = "armv5t"
    ARMV5E = "armv5e"
    ARMV5TE = "armv5te"
    ARMV5TEJ = "armv5tej"
    ARMV6 = "armv6"
    ARMV6J = "armv6j"
    ARMV6K = "armv6k"
    ARMV6Z = "armv6z"
    ARMV6KZ = "armv6kz"
    ARMV6ZK = "armv6zk"
    ARMV6T2 = "armv6t2"
    ARMV6_M = "armv6-m"
    ARMV6S_M = "armv6s-m"
    ARMV7 = "armv7"
    ARMV7_A = "armv7-a"
    ARMV7VE = "armv7ve"
    ARMV7_R = "armv7-r"
    ARMV7_M = "armv7-m"
    ARMV7E_M = "armv7e-m"
    ARMV8_A = "armv8-a"
    ARMV8_1_A = "armv8.1-a"
    ARMV8_2_A = "armv8.2-a"
    ARMV8_3_A = "armv8.3-a"
    ARMV8_4_A = "armv8.4-a"
    ARMV8_5_A = "armv8.5-a"
    ARMV8_M_BASE = "armv8-m.base"
    ARMV8_M_MAIN = "armv8-m.main"
    ARMV8_R = "armv8-r"
    IWMMXT = "iwmmxt"
    IWMMXT2 = "iwmmxt2"
    UNKNOWN = "unknown"


class UArch(Enum):
    ARM1020E = "arm1020e"
    ARM1020T = "arm1020t"
    ARM1022E = "arm1022e"
    ARM1026EJ_S = "arm1026ej-s"
    ARM10E = "arm10e"
    ARM10TDMI = "arm10tdmi"
    ARM1136JF_S = "arm1136jf-s"
    ARM1136J_S = "arm1136j-s"
    ARM1156T2F_S = "arm1156t2f-s"
    ARM1156T2_S = "arm1156t2-s"
    ARM1176JZF_S = "arm1176jzf-s"
    ARM1176JZ_S = "arm1176jz-s"
    ARM2 = "arm2"
    ARM250 = "arm250"
    ARM3 = "arm3"
    ARM6 = "arm6"
    ARM60 = "arm60"
    ARM600 = "arm600"
    ARM610 = "arm610"
    ARM620 = "arm620"
    ARM7 = "arm7"
    ARM70 = "arm70"
    ARM700 = "arm700"
    ARM700I = "arm700i"
    ARM710 = "arm710"
    ARM7100 = "arm7100"
    ARM710C = "arm710c"
    ARM710T = "arm710t"
    ARM720 = "arm720"
    ARM720T = "arm720t"
    ARM740T = "arm740t"
    ARM7500 = "arm7500"
    ARM7500FE = "arm7500fe"
    ARM7D = "arm7d"
    ARM7DI = "arm7di"
    ARM7DM = "arm7dm"
    ARM7DMI = "arm7dmi"
    ARM7M = "arm7m"
    ARM7TDMI = "arm7tdmi"
    ARM7TDMI_S = "arm7tdmi-s"
    ARM8 = "arm8"
    ARM810 = "arm810"
    ARM9 = "arm9"
    ARM920 = "arm920"
    ARM920T = "arm920t"
    ARM922T = "arm922t"
    ARM926EJ_S = "arm926ej-s"
    ARM940T = "arm940t"
    ARM946E_S = "arm946e-s"
    ARM966E_S = "arm966e-s"
    ARM968E_S = "arm968e-s"
    ARM9E = "arm9e"
    ARM9TDMI = "arm9tdmi"
    CARMEL = "carmel"
    CORTEX_A12 = "cortex-a12"
    CORTEX_A15 = "cortex-a15"
    CORTEX_A17 = "cortex-a17"
    CORTEX_A32 = "cortex-a32"
    CORTEX_A35 = "cortex-a35"
    CORTEX_A5 = "cortex-a5"
    CORTEX_A53 = "cortex-a53"
    CORTEX_A55 = "cortex-a55"
    CORTEX_A57 = "cortex-a57"
    CORTEX_A7 = "cortex-a7"
    CORTEX_A72 = "cortex-a72"
    CORTEX_A73 = "cortex-a73"
    CORTEX_A75 = "cortex-a75"
    CORTEX_A76 = "cortex-a76"
    CORTEX_A77 = "cortex-a77"
    CORTEX_A8 = "cortex-a8"
    CORTEX_A9 = "cortex-a9"
    CORTEX_M0 = "cortex-m0"
    CORTEX_M0PLUS = "cortex-m0plus"
    CORTEX_M0PLUS_SMALL_MULTIPLY = "cortex-m0plus.small-multiply"
    CORTEX_M0_SMALL_MULTIPLY = "cortex-m0.small-multiply"
    CORTEX_M1 = "cortex-m1"
    CORTEX_M1_SMALL_MULTIPLY = "cortex-m1.small-multiply"
    CORTEX_M23 = "cortex-m23"
    CORTEX_M3 = "cortex-m3"
    CORTEX_M33 = "cortex-m33"
    CORTEX_M4 = "cortex-m4"
    CORTEX_M7 = "cortex-m7"
    CORTEX_R4 = "cortex-r4"
    CORTEX_R4F = "cortex-r4f"
    CORTEX_R5 = "cortex-r5"
    CORTEX_R52 = "cortex-r52"
    CORTEX_R7 = "cortex-r7"
    CORTEX_R8 = "cortex-r8"
    DENVER = "denver"
    DENVER2 = "denver2"
    EP9312 = "ep9312"
    EXYNOS_M1 = "exynos-m1"
    FA526 = "fa526"
    FA606TE = "fa606te"
    FA626 = "fa626"
    FA626TE = "fa626te"
    FA726TE = "fa726te"
    FALKOR = "falkor"
    FMP626 = "fmp626"
    GENERIC_ARMV7_A = "generic-armv7-a"
    IWMMXT = "iwmmxt"
    IWMMXT2 = "iwmmxt2"
    MARVELL_PJ4 = "marvell-pj4"
    ARM11_MPCORE = "arm11-mpcore"
    ARM11_MPCORENOVFP = "arm11-mpcorenovfp"
    QDF24XX = "qdf24xx"
    SAPHIRA = "saphira"
    STRONGARM = "strongarm"
    STRONGARM110 = "strongarm110"
    STRONGARM1100 = "strongarm1100"
    STRONGARM1110 = "strongarm1110"
    THUNDERX = "thunderx"
    THUNDERX2T99 = "thunderx2t99"
    THUNDERX2T99P1 = "thunderx2t99p1"
    THUNDERXT81 = "thunderxt81"
    THUNDERXT83 = "thunderxt83"
    THUNDERXT88 = "thunderxt88"
    THUNDERXT88P1 = "thunderxt88p1"
    VULCAN = "vulcan"
    XGENE1 = "xgene1"
    XSCALE = "xscale"
    NEOVERSE_N1 = "neoverse-n1"
    NEOVERSE_E1 = "neoverse-e1"
    BRAHMA_B15 = "brahma-b15"
    BRAHMA_B32 = "brahma-b32"
    BRAHMA_B53 = "brahma-b53"
    SA110 = "sa110"
    SA1100 = "sa1100"
    SCORPION = "scorpion"
    KRAIT = "krait"
    KRYO = "kryo"
    TSV110 = "tsv110"
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


class Vendor(Enum):
    APM = "apm"
    ARM = "arm"
    BROADCOM = "broadcom"
    CAVIUM = "cavium"
    DEC = "dec"
    FARADAY = "faraday"
    GOOGLE = "google"
    HISILICON = "hisilicon"
    INFINEON = "infineon"
    INTEL = "intel"
    MARVELL = "marvell"
    NVIDIA = "nvidia"
    QUALCOMM = "qualcomm"
    SAMSUNG = "samsung"
    EKUT = "ekut"
    UNKNOWN = "unknown"
