import re
import collections
from typing import List, NamedTuple, Tuple, Dict, Union, Any
from fabric import Connection
import logging


from ..model import CoreModel
from .cpuinfo_arm import implementers as arm_implementers, uarch_to_isa
from ..model.common import ISA, UArch, ISAExtension, Vendor


def _cpuinfo(text: str) -> List[CoreModel]:
    lines = text.split("\n")

    current_dict: Dict[str, Any] = {}
    cpus: List[CoreModel] = []
    for line in lines:
        m = re.match(r"processor\s+: (\d+)", line)
        if m:
            if current_dict:
                if current_dict["isa"] == ISA.UNKNOWN:
                    if current_dict["uarch"] in uarch_to_isa:
                        current_dict["isa"] = uarch_to_isa[
                            current_dict["uarch"]
                        ]
                current_dict["description"] = current_dict[
                    "description"
                ] + " (microarchitecture: {})".format(
                    current_dict["uarch"].value
                )
                cpus.append(CoreModel(**current_dict))
            current_dict = {}
            current_dict["id"] = int(m.group(1))

        m = re.match(r"model name\s+: (.*)", line)
        if m:
            current_dict["description"] = str(m.group(1)).strip()

        m = re.match(r"CPU implementer\s*: (\S+)", line)
        if m:
            implementer_key = int(m.group(1), 16)

            vendor = Vendor.UNKNOWN
            if implementer_key in arm_implementers:
                vendor = arm_implementers[implementer_key][0]

            current_dict["vendor"] = vendor

        m = re.match(r"CPU architecture\s*: (\S+)", line)
        if m:
            architecture_key = int(m.group(1), 10)
            isa = ISA.UNKNOWN
            current_dict["isa"] = isa

        m = re.match(r"CPU variant\s*: (\S+)", line)
        if m:
            variant_key = int(m.group(1), 16)
            # TODO: Currently we do nothing with this information

        m = re.match(r"CPU part\s*: (\S+)", line)
        if m:
            part_key = int(m.group(1), 16)

            uarch = UArch.UNKNOWN
            if implementer_key in arm_implementers:
                if part_key in arm_implementers[implementer_key][1]:
                    uarch = arm_implementers[implementer_key][1][part_key]

            current_dict["uarch"] = uarch

    if current_dict:

        if current_dict["isa"] == ISA.UNKNOWN:
            if current_dict["uarch"] in uarch_to_isa:
                current_dict["isa"] = uarch_to_isa[current_dict["uarch"]]
        current_dict["description"] = current_dict[
            "description"
        ] + " (microarchitecture: {})".format(current_dict["uarch"].value)
        cpus.append(CoreModel(**current_dict))

    return cpus


def cpuinfo(con: Connection) -> List[CoreModel]:
    cpus: List[CoreModel] = []

    result = con.run("cat /proc/cpuinfo", hide="stdout", warn=True)
    if result.return_code != 0:
        return []

    return _cpuinfo(result.stdout)
