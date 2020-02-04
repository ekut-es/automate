from typing import Dict, Tuple


arm_cpus: Dict[int, str] = {
    0x810: "arm810",
    0x920: "arm920",
    0x922: "arm922t",
    0x926: "arm926ej_s",
    0x940: "arm940t",
    0x946: "arm946e_s",
    0x966: "arm966e_s",
    0xA20: "arm1020e",
    0xA22: "arm1022e",
    0xA26: "arm1026ej_s",
    0xB02: "arm11_mpcore",
    0xB36: "arm1136j_s",
    0xB56: "arm1156t2_s",
    0xB76: "arm1176jz_s",
    0xC05: "cortex_a5",
    0xC07: "cortex_a7",
    0xC08: "cortex_a8",
    0xC09: "cortex_a9",
    0xC0D: "cortex_a17",
    0xC0F: "cortex_a15",
    0xC0E: "cortex_a17",
    0xC14: "cortex_r4",
    0xC15: "cortex_r5",
    0xC17: "cortex_r7",
    0xC18: "cortex_r8",
    0xC20: "cortex_m0",
    0xC21: "cortex_m1",
    0xC23: "cortex_m3",
    0xC24: "cortex_m4",
    0xC27: "cortex_m7",
    0xC60: "cortex_m0plus",
    0xD01: "cortex_a32",
    0xD03: "cortex_a53",
    0xD04: "cortex_a35",
    0xD05: "cortex_a55",
    0xD07: "cortex_a57",
    0xD08: "cortex_a72",
    0xD09: "cortex_a73",
    0xD0A: "cortex_a75",
    0xD0B: "cortex_a76",
    0xD0C: "neoverse_n1",
    0xD13: "cortex_r52",
    0xD20: "cortex_m23",
    0xD21: "cortex_m33",
    0xD4A: "neoverse_e1",
}

broadcom_cpus: Dict[int, str] = {
    0x00F: "brahma_b15",
    0x100: "brahma_b53",
    0x516: "thunderx2t99",
}

dec_cpus: Dict[int, str] = {0xA10: "sa110", 0xA11: "sa1100"}

cavium_cpus: Dict[int, str] = {
    0x0A0: "thunderx",
    0x0A1: "thunderxt88",
    0x0A2: "thunderxt81",
    0x0A3: "thunderxt83",
    0x0AF: "thunderx2_99",
}

apm_cpu: Dict[int, str] = {0x000: "xgene1"}

qualcom_cpus: Dict[int, str] = {
    0x00F: "scorpion",
    0x02D: "scorpion",
    0x04D: "krait",
    0x06F: "krait",
    0x201: "kryo",
    0x205: "kryo",
    0x211: "kryo",
    0x800: "falkor_v1_kryo",
    0x801: "kryo_v2",
    0xC00: "falkor",
    0xC01: "saphira",
}

samsung_cpus: Dict[int, str] = {0x001: "exynos_m1"}

nvidia_cpus: Dict[int, str] = {
    0x000: "denver",
    0x003: "denver2",
    0x004: "carmel",
}

marvell_cpus: Dict[int, str] = {
    0x131: "feroceon_88fr131",
    0x581: "pj4_pj4b",
    0x584: "pj4b_mp",
}

faraday_cpus: Dict[int, str] = {0x526: "fa526", 0x626: "fa626"}

intel_cpus: Dict[int, str] = {
    0x200: "i80200",
    0x210: "pxa250a",
    0x212: "pxa210a",
    0x242: "i80321_400",
    0x243: "i80321_600",
    0x290: "pxa250b_pxa26x",
    0x292: "pxa210b",
    0x2C2: "i80321_400_b0",
    0x2C3: "i80321_600_b0",
    0x2D0: "pxa250c/pxa255/pxa26x",
    0x2D2: "pxa210c",
    0x411: "pxa27x",
    0x41C: "ipx425_533",
    0x41D: "ipx425_400",
    0x41F: "ipx425_266",
    0x682: "pxa32x",
    0x683: "pxa930/pxa935",
    0x688: "pxa30x",
    0x689: "pxa31x",
    0xB11: "sa1110",
    0xC12: "ipx1200",
}

hisilicon_cpus: Dict[int, str] = {0xD01: "tsv110"}


infineon_cpus: Dict[int, str] = {}


implementers: Dict[int, Tuple[str, Dict[int, str]]] = {
    0x41: ("arm", arm_cpus),
    0x42: ("broadcom", broadcom_cpus),
    0x43: ("cavium", cavium_cpus),
    0x44: ("dec", dec_cpus),
    0x48: ("hisilicon", hisilicon_cpus),
    0x49: ("infineon", infineon_cpus),
    0x4E: ("nvidia", nvidia_cpus),
    0x50: ("apm", arm_cpus),
    0x51: ("qualcom", qualcom_cpus),
    0x53: ("qualcom", samsung_cpus),
    0x56: ("marvell", marvell_cpus),
    0x66: ("faraday", faraday_cpus),
    0x69: ("intel", intel_cpus),
}


# TODO: there should be a better way to do this
# Source: https://developer.arm.com/ip-products/processors/cortex-a
uarch_to_isa: Dict[str, str] = {
    "cortex_a12": "armv7_a",
    "cortex_a15": "armv7_a",
    "cortex_a17": "armv7_a",
    "cortex_a32": "armv8_a",
    "cortex_a35": "armv8_a",
    "cortex_a5": "armv7_a",
    "cortex_a53": "armv8_a",
    "cortex_a55": "armv8_2_a",
    "cortex_a57": "armv8_a",
    "cortex_a7": "armv7_a",
    "cortex_a72": "armv8_a",
    "cortex_a73": "armv8_a",
    "cortex_a75": "armv8_2_a",
    "cortex_a76": "armv8_2_a",
    "cortex_a77": "armv8_2_a",
    "cortex_a9": "armv7_a",
    "denver": "armv8_a",
    "denver2": "armv8_a",
    "carmel": "armv8_2_a",
}
