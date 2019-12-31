from typing import Dict, List, Union

from ..model.common import Machine
from .. import board
from .. import compiler


class FilteredKernelOption:
    def __init__(self, option: str) -> None:
        self.option = option

    def filter(self, board: "board.Board") -> bool:
        raise NotImplementedError("filter has not been implemented")


class MachineOption(FilteredKernelOption):
    def __init__(
        self, option: str, machines: List[Union[Machine, str]]
    ) -> None:
        machines = [
            m if isinstance(m, Machine) else Machine(m) for m in machines
        ]

        self.machines = set(machines)

        super(MachineOption, self).__init__(option)

    def filter(self, board: "board.Board") -> bool:
        return board.os.machine in self.machines


class KernelConfigBuilder:
    def __init__(
        self, board: "board.Board", cross_compiler: "compiler.CrossCompiler"
    ) -> None:
        self.board = board
        self.cross_compiler = cross_compiler
        self._predefined_configs: Dict[str, List[str]] = {
            "default": [
                # Base Options
                "CONFIG_PROC_KCORE=y",
                "CONFIG_IKCONFIG=y",
                "CONFIG_IKCONFIG_PROC=y",
                "CONFIG_HW_PERF_EVENTS=y",
                "CONFIG_KEXEC=y",
                "CONFIG_KEXEC_CORE=y",
                "CONFIG_NO_HZ_FULL=y",
                "CONFIG_MAGIC_SYSRQ=y",
                "CONFIG_MAGIC_SYSRQ_DEFAULT_ENABLE=0x1",
                # Coresight
                MachineOption("CONFIG_CORESIGHT=y", ["aarch64", "arm"]),
                MachineOption(
                    "CONFIG_CORESIGHT_LINKS_AND_SINKS=y", ["aarch64", "arm"]
                ),
                MachineOption(
                    "CONFIG CONFIG_CORESIGHT_SOURCE_ETM4X=y", ["aarch64", "arm"]
                ),
                MachineOption("CONFIG_CORESIGHT_STM=y", ["aarch64", "arm"]),
                MachineOption(
                    "CONFIG_CORESIGHT_QCOM_REPLICATOR=y", ["aarch64", "arm"]
                ),
                MachineOption(
                    "CONFIG_CORESIGHT_LINK_AND_SINK_TMC=y", ["aarch64", "arm"]
                ),
                MachineOption(
                    "CONFIG_CORESIGHT_SINK_TPIU=y CONFIG_CORESIGHT_SINK_ETBV10=y",
                    ["aarch64", "arm"],
                ),
                # BPF
                "CONFIG_BPF=y",
                "CONFIG_BPF_JIT=y",
                "CONFIG_HAVE_EBPF_JIT=y",
                "CONFIG_BPF_SYSCALL=y",
            ]
        }

    def _filter_options(self, options) -> List[str]:
        res = []
        for option in options:
            if isinstance(option, str):
                res.append(option)
            else:
                if option.filter(self.board):
                    res.append(option.option)

        return res

    def predefined_configs(self):
        """Return all predefined configs that are applicable to a board

        Returns:
           An iterable of tuple of string(name) and list of string [kernel config options]
        """

        for k, v in self._predefined_configs:
            yield (k, self._filter_options(v))

    def predefined_config(self, name: str) -> List[str]:
        """Search for predefined config options with given name"""
        for config_name, config in self.predefined_configs():
            if config_name == name:
                return config

        raise Exception("Could not find predefined config {}".format(name))

    def predefined_config_fragment(self, name: str) -> str:
        fragment = ""
        try:
            fragment = "\n".join(self.predefined_config(name))
        except:
            pass
        return fragment


__all__ = ["KernelConfigBuilder"]
