import re
from typing import Any, Dict, List

from fabric import Connection

from ..model import CoreModel
from .cpuinfo_arm import implementers as arm_implementers
from .cpuinfo_arm import uarch_to_isa

__all__ = ["cpuinfo"]


def _cpuinfo(text: str) -> List[CoreModel]:
    """Parse a /proc/cpuinfo file to a list of core models

    # Arguments
    text: contents of cpuinfo file

    # Returns
    List of Core Models for the cpus in cpuinfo
    """

    lines = text.split("\n")

    current_dict: Dict[str, Any] = {}
    cpus: List[CoreModel] = []
    for line in lines:
        m = re.match(r"processor\s+: (\d+)", line)
        if m:
            if current_dict:
                if "isa" not in current_dict or not current_dict["isa"]:
                    if current_dict["uarch"] in uarch_to_isa:
                        current_dict["isa"] = uarch_to_isa[
                            current_dict["uarch"]
                        ]
                current_dict["description"] = current_dict[
                    "description"
                ] + " (microarchitecture: {})".format(current_dict["uarch"])
                cpus.append(CoreModel(**current_dict))
            current_dict = {"description": ""}
            current_dict["num"] = int(m.group(1))
            current_dict["isa"] = ""

        m = re.match(r"model name\s+: (.*)", line)
        if m:
            current_dict["description"] = str(m.group(1)).strip()

        m = re.match(r"CPU implementer\s*: (\S+)", line)
        if m:
            implementer_key = int(m.group(1), 16)

            vendor = ""
            if implementer_key in arm_implementers:
                vendor = arm_implementers[implementer_key][0]

            current_dict["vendor"] = vendor

        m = re.match(r"CPU part\s*: (\S+)", line)
        if m:
            part_key = int(m.group(1), 16)

            uarch = ""
            if implementer_key in arm_implementers:
                if part_key in arm_implementers[implementer_key][1]:
                    uarch = arm_implementers[implementer_key][1][part_key]

            current_dict["uarch"] = uarch

        m = re.match(r"Features\s*: (.*)", line)
        if m:
            features = m.group(1).split()

            current_dict["extensions"] = list(sorted(features))

    if current_dict:

        if "isa" not in current_dict or not current_dict["isa"]:
            if current_dict["uarch"] in uarch_to_isa:
                current_dict["isa"] = uarch_to_isa[current_dict["uarch"]]
        current_dict["description"] = current_dict[
            "description"
        ] + " (microarchitecture: {})".format(current_dict["uarch"])
        cpus.append(CoreModel(**current_dict))

    return cpus


def cpuinfo(con: Connection) -> List[CoreModel]:
    """Parse remote CPU info over ssh connection

    # Arguments
    con: fabric.Connection for the

    # Returns
    A list of CoreModel with the parsed cpuinfos
    """
    result = con.run("cat /proc/cpuinfo", hide="stdout", warn=True)
    if result.return_code != 0:
        return []

    return _cpuinfo(result.stdout)
