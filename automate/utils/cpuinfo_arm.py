from ..model.common import Vendor, UArch, ISA

from typing import Dict, Tuple

arm_cpus: Dict[int, UArch] = {
    0x810: UArch.ARM810,
    0x920: UArch.ARM920,
    0x922: UArch.ARM922T,
    0x926: UArch.ARM926EJ_S,
    0x940: UArch.ARM940T,
    0x946: UArch.ARM946E_S,
    0x966: UArch.ARM966E_S,
    0xA20: UArch.ARM1020E,
    0xA22: UArch.ARM1022E,
    0xA26: UArch.ARM1026EJ_S,
    0xB02: UArch.ARM11_MPCORE,
    0xB36: UArch.ARM1136J_S,
    0xB56: UArch.ARM1156T2_S,
    0xB76: UArch.ARM1176JZ_S,
    0xC05: UArch.CORTEX_A5,
    0xC07: UArch.CORTEX_A7,
    0xC08: UArch.CORTEX_A8,
    0xC09: UArch.CORTEX_A9,
    0xC0D: UArch.CORTEX_A17,
    0xC0F: UArch.CORTEX_A15,
    0xC0E: UArch.CORTEX_A17,
    0xC14: UArch.CORTEX_R4,
    0xC15: UArch.CORTEX_R5,
    0xC17: UArch.CORTEX_R7,
    0xC18: UArch.CORTEX_R8,
    0xC20: UArch.CORTEX_M0,
    0xC21: UArch.CORTEX_M1,
    0xC23: UArch.CORTEX_M3,
    0xC24: UArch.CORTEX_M4,
    0xC27: UArch.CORTEX_M7,
    0xC60: UArch.CORTEX_M0PLUS,
    0xD01: UArch.CORTEX_A32,
    0xD03: UArch.CORTEX_A53,
    0xD04: UArch.CORTEX_A35,
    0xD05: UArch.CORTEX_A55,
    0xD07: UArch.CORTEX_A57,
    0xD08: UArch.CORTEX_A72,
    0xD09: UArch.CORTEX_A73,
    0xD0A: UArch.CORTEX_A75,
    0xD0B: UArch.CORTEX_A76,
    0xD0C: UArch.NEOVERSE_N1,
    0xD13: UArch.CORTEX_R52,
    0xD20: UArch.CORTEX_M23,
    0xD21: UArch.CORTEX_M33,
    0xD4A: UArch.NEOVERSE_E1,
}

broadcom_cpus: Dict[int, UArch] = {
    0x00F: UArch.BRAHMA_B15,
    0x100: UArch.BRAHMA_B53,
    0x516: UArch.THUNDERX2T99,
}

dec_cpus: Dict[int, UArch] = {0xA10: UArch.SA110, 0xA11: UArch.SA1100}

cavium_cpus: Dict[int, UArch] = {
    0x0A0: UArch.THUNDERX,
    0x0A1: UArch.THUNDERXT88,
    0x0A2: UArch.THUNDERXT81,
    0x0A3: UArch.THUNDERXT83,
    #      0X0AF:  UArch.THUNDERX2_99  ,
}

apm_cpu: Dict[int, UArch] = {0x000: UArch.XGENE1}

qualcom_cpus: Dict[int, UArch] = {
    0x00F: UArch.SCORPION,
    0x02D: UArch.SCORPION,
    0x04D: UArch.KRAIT,
    0x06F: UArch.KRAIT,
    0x201: UArch.KRYO,
    0x205: UArch.KRYO,
    0x211: UArch.KRYO,
    #      0X800:  UArch.FALKOR_V1_KRYO  ,
    #      0X801:  UArch.KRYO_V2  ,
    0xC00: UArch.FALKOR,
    0xC01: UArch.SAPHIRA,
}

samsung_cpus: Dict[int, UArch] = {0x001: UArch.EXYNOS_M1}

nvidia_cpus: Dict[int, UArch] = {
    0x000: UArch.DENVER,
    0x003: UArch.DENVER2,
    0x004: UArch.CARMEL,
}

marvell_cpus: Dict[int, UArch] = {
    #      0X131:  UArch.FEROCEON_88FR131  ,
    #      0X581:  UArch.PJ4_PJ4B  ,
    #      0X584:  UArch.PJ4B_MP  ,
}

faraday_cpus: Dict[int, UArch] = {
    #      0X526:  UArch.FA526 ,
    #      0X626:  UArch.FA626  ,
}

intel_cpus: Dict[int, UArch] = {
    #      0X200:  UArch.I80200  ,
    #      0X210:  UArch.PXA250A  ,
    #      0X212:  UArch.PXA210A  ,
    #      0X242:  UArch.I80321_400  ,
    #      0X243:  UArch.I80321_600  ,
    #      0X290:  UArch.PXA250B_PXA26X  ,
    #      0X292:  UArch.PXA210B  ,
    #      0X2C2:  UArch.I80321_400_B0  ,
    #      0X2C3:  UArch.I80321_600_B0  ,
    #      0X2D0:  UArch.PXA250C/PXA255/PXA26X  ,
    #      0X2D2:  UArch.PXA210C  ,
    #      0X411:  UArch.PXA27X  ,
    #      0X41C:  UArch.IPX425_533  ,
    #      0X41D:  UArch.IPX425_400  ,
    #      0X41F:  UArch.IPX425_266  ,
    #      0X682:  UArch.PXA32X  ,
    #      0X683:  UArch.PXA930/PXA935  ,
    #      0X688:  UArch.PXA30X  ,
    #      0X689:  UArch.PXA31X  ,
    #      0XB11:  UArch.SA1110  ,
    #      0XC12:  UArch.IPX1200  ,
}

hisilicon_cpus: Dict[int, UArch] = {0xD01: UArch.TSV110}


infineon_cpus: Dict[int, UArch] = {}


implementers: Dict[int, Tuple[Vendor, Dict[int, UArch]]] = {
    0x41: (Vendor.ARM, arm_cpus),
    0x42: (Vendor.BROADCOM, broadcom_cpus),
    0x43: (Vendor.CAVIUM, cavium_cpus),
    0x44: (Vendor.DEC, dec_cpus),
    0x48: (Vendor.HISILICON, hisilicon_cpus),
    0x49: (Vendor.INFINEON, infineon_cpus),
    0x4E: (Vendor.NVIDIA, nvidia_cpus),
    0x50: (Vendor.APM, arm_cpus),
    0x51: (Vendor.QUALCOMM, qualcom_cpus),
    0x53: (Vendor.SAMSUNG, samsung_cpus),
    0x56: (Vendor.MARVELL, marvell_cpus),
    0x66: (Vendor.FARADAY, faraday_cpus),
    0x69: (Vendor.INTEL, intel_cpus),
}


# TODO: there should be a better way to do this
# Source: https://developer.arm.com/ip-products/processors/cortex-a
uarch_to_isa: Dict[UArch, ISA] = {
    UArch.CORTEX_A12: ISA.ARMV7_A,
    UArch.CORTEX_A15: ISA.ARMV7_A,
    UArch.CORTEX_A17: ISA.ARMV7_A,
    UArch.CORTEX_A32: ISA.ARMV8_A,
    UArch.CORTEX_A35: ISA.ARMV8_A,
    UArch.CORTEX_A5: ISA.ARMV7_A,
    UArch.CORTEX_A53: ISA.ARMV8_A,
    UArch.CORTEX_A55: ISA.ARMV8_2_A,
    UArch.CORTEX_A57: ISA.ARMV8_A,
    UArch.CORTEX_A7: ISA.ARMV7_A,
    UArch.CORTEX_A72: ISA.ARMV8_A,
    UArch.CORTEX_A73: ISA.ARMV8_A,
    UArch.CORTEX_A75: ISA.ARMV8_2_A,
    UArch.CORTEX_A76: ISA.ARMV8_2_A,
    UArch.CORTEX_A77: ISA.ARMV8_2_A,
    UArch.CORTEX_A9: ISA.ARMV7_A,
    UArch.DENVER: ISA.ARMV8_A,
    UArch.DENVER2: ISA.ARMV8_A,
    UArch.CARMEL: ISA.ARMV8_2_A,
}
