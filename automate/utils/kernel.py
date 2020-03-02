from typing import Dict, Generator, List, Tuple, Union

from .. import board, compiler
from ..model.common import Machine

__all__ = ["KernelConfigBuilder", "KernelData"]


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
        return board.os.triple.machine in self.machines


class PredefinedNotFoundException(Exception):
    pass


class KernelConfigBuilder:
    def __init__(
        self, board: "board.Board", cross_compiler: "compiler.CrossCompiler"
    ) -> None:
        self.board = board
        self.cross_compiler = cross_compiler
        self._predefined_configs: Dict[str, List[Union[MachineOption, str]]] = {
            "default": [
                # Base Options
                "CONFIG_PROC_KCORE=y",
                "CONFIG_IKCONFIG=y",
                "CONFIG_IKCONFIG_PROC=y",
                "CONFIG_IKHEADERS=m",
                "CONFIG_HW_PERF_EVENTS=y",
                "CONFIG_KEXEC=y",
                "CONFIG_KEXEC_CORE=y",
                "CONFIG_NO_HZ_FULL=y",
                "CONFIG_MAGIC_SYSRQ=y",
                "CONFIG_MAGIC_SYSRQ_DEFAULT_ENABLE=0x1",
                "CONFIG_HOTPLUG_CPU=y",
                # Coresight
                MachineOption("CONFIG_CORESIGHT=y", ["aarch64", "arm"]),
                MachineOption(
                    "CONFIG_CORESIGHT_LINKS_AND_SINKS=y", ["aarch64", "arm"]
                ),
                MachineOption(
                    "CONFIG_CORESIGHT_SOURCE_ETM4X=y", ["aarch64", "arm"]
                ),
                MachineOption("CONFIG_CORESIGHT_STM=y", ["aarch64", "arm"]),
                MachineOption(
                    "CONFIG_CORESIGHT_QCOM_REPLICATOR=y", ["aarch64", "arm"]
                ),
                MachineOption(
                    "CONFIG_CORESIGHT_LINK_AND_SINK_TMC=y", ["aarch64", "arm"]
                ),
                MachineOption(
                    "CONFIG_CORESIGHT_SINK_TPIU=y", ["aarch64", "arm"]
                ),
                MachineOption(
                    "CONFIG_CORESIGHT_SINK_ETBV10=y", ["aarch64", "arm"]
                ),
                MachineOption(
                    "CONFIG_CORESIGHT_SOURCE_ETM3X=y", ["aarch64", "arm"]
                ),
                MachineOption(
                    "CONFIG_CORESIGHT_DYNAMIC_REPLICATOR=y", ["aarch64", "arm"]
                ),
                MachineOption("CONFIG_CORESIGHT_CATU=y", ["aarch64", "arm"]),
                MachineOption(
                    "CONFIG_CORESIGHT_CPU_DEBUG=y", ["aarch64", "arm"]
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

    def predefined_configs(
        self,
    ) -> Generator[Tuple[str, List[str]], None, None]:
        """Return all predefined configs that are applicable to a board

        Returns:
           An iterable of tuple of string(name) and list of string [kernel config options]
        """

        for k, v in self._predefined_configs.items():
            yield (k, self._filter_options(v))

    def predefined_config(self, name: str) -> List[str]:
        """Search for predefined config options with given name"""
        for config_name, config in self.predefined_configs():
            if config_name == name:
                return config

        raise PredefinedNotFoundException(
            "Could not find predefined config {}".format(name)
        )

    def predefined_config_fragment(self, name: str) -> str:
        fragment = ""
        try:
            fragment = "\n".join(self.predefined_config(name))
        except PredefinedNotFoundException:
            pass
        return fragment


class KernelData(object):
    """ Provides collection of calculated kernel data """

    def __init__(self, board, kernel_desc):
        self.board = board
        self.kernel_desc = kernel_desc

    @property
    def srcdir(self):
        return self.kernel_desc.kernel_srcdir

    @property
    def arch(self):
        arch = (
            self.board.os.triple.machine.value
            if self.board.os.triple.machine.value != "aarch64"
            else "arm64"
        )
        return arch

    @property
    def shared_data_dir(self):
        """Location for shared kernel sources and cached deploy and build packages"""
        kernel_shared_dir = self.kernel_desc.kernel_source.parent

        return kernel_shared_dir

    @property
    def deploy_package_name(self):
        """Name of the kernel deploy archive"""
        return "kernel-{0}.tar.gz".format(self.kernel_desc.name)

    @property
    def deploy_package_path(self):
        return self.shared_data_dir / self.deploy_package_name

    @property
    def build_cache_name(self):
        """Name of the kernel build cache archive"""
        return "kernel-build-{}.tar.bz".format(self.kernel_desc.name)

    @property
    def build_cache_path(self):
        return self.shared_data_dir / self.build_cache_name
