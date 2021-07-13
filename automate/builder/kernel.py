import os.path
from pathlib import Path
from typing import Dict, Optional

from .. import compiler
from ..utils import untar
from ..utils.kernel import KernelConfigBuilder, KernelData
from ..utils.network import rsync
from ..utils.uboot import build_ubimage
from .builder import BaseBuilder, BuilderState


class KernelBuilder(BaseBuilder):
    def _kernel_desc(self):
        board = self.board

        kernel_desc = None
        for kernel in board.os.kernels:
            if kernel.name == self._kernel_name():
                kernel_desc = kernel
                break

        if kernel_desc is None:
            raise Exception(
                "Could not find config with id: {} for board {}".format(
                    self._kernel_name(), board.name
                )
            )

        return kernel_desc

    def _kernel_data(self) -> KernelData:
        """Computed kernel data"""

        return KernelData(self.board, self._kernel_desc())

    def _kernel_name(self) -> str:
        """Name for current kernel config"""

        assert self.state.kernel is not None
        return str(self.state.kernel["kernel_name"])

    def _arch(self) -> str:
        """Arch argument"""

        assert self.state.kernel is not None
        return str(self.state.kernel["arch"])

    def _cross_compile(self) -> str:
        """COSS_COMPILE argument for kernel builds"""

        assert self.state.kernel is not None
        return str(self.state.kernel["cross_compile"])

    def configure(self, kernel_name, cross_compiler=None):
        """configure kernel build
        
        # Arguments
        kernel_name: name of the kernel config (see Metadata)
        cross_compiler: cross_compiler object to use
        """

        if cross_compiler is None:
            cross_compiler = self.board.compiler()

        super(KernelBuilder, self).configure(cross_compiler=cross_compiler)

        self._mkbuilddir()

        self.state.kernel = {}
        self.state.kernel["arch"] = (
            cross_compiler.machine.value
            if cross_compiler.machine.value != "aarch64"
            else "arm64"
        )
        self.state.kernel["kernel_name"] = kernel_name
        self.state.kernel["cross_compile"] = os.path.join(
            cross_compiler.bin_path, cross_compiler.prefix
        )

        kernel_desc = self._kernel_desc()
        self.state.srcdir = self.builddir / kernel_desc.kernel_srcdir
        self.state.prefix = Path("/")

        self._save_state()

        with self.context.cd(str(self.builddir)):
            srcdir = self.srcdir

            if not Path(srcdir).exists():
                self.context.run("cp {} .".format(kernel_desc.kernel_source))
                kernel_archive = (
                    self.builddir / Path(kernel_desc.kernel_source).name
                )
                untar(kernel_archive, self.builddir)

            with self.context.cd(str(srcdir)):

                self.context.run(
                    "cp {} .config".format(kernel_desc.kernel_config)
                )

                self.context.run(
                    "make ARCH={0} CROSS_COMPILE={1} olddefconfig".format(
                        self._arch(), self._cross_compile()
                    )
                )

                config_builder = KernelConfigBuilder(self.board, cross_compiler)
                config_fragment = srcdir / ".config_fragment"
                with config_fragment.open("w") as fragment:
                    fragment_str = config_builder.predefined_config_fragment(
                        kernel_name
                    )
                    print(fragment_str)
                    fragment.write(fragment_str)

                with self.context.prefix(
                    "export ARCH={0} && export CROSS_COMPILE={1}".format(
                        self._arch(), self._cross_compile()
                    )
                ):
                    self.context.run(
                        "./scripts/kconfig/merge_config.sh .config .config_fragment"
                    )

                self.context.run(
                    "cp .config {}".format(kernel_desc.kernel_config)
                )

    def build(self):
        """Build kernel"""

        self._mkbuilddir()
        kernel_desc = self._kernel_desc()

        build_path = Path(self.builddir)
        install_path = build_path / "install"
        boot_path = install_path / "boot"
        self.context.run("rm -rf {}".format(install_path))

        with self.context.cd(str(self.builddir)):
            srcdir = kernel_desc.kernel_srcdir
            with self.context.cd(str(srcdir)):

                self.logger.info("Trying build")

                self.context.run(
                    "make -j {2} ARCH={0} CROSS_COMPILE={1} all".format(
                        self._arch(),
                        self._cross_compile(),
                        self._num_build_cpus(),
                    )
                )

                self.logger.info("Trying dtbs install target")

                dtb_install_result = self.context.run(
                    "make dtbs_install ARCH={0} CROSS_COMPILE={1} INSTALL_DTBS_PATH={2}/lib/firmware/{3}/device-tree/".format(
                        self._arch(),
                        self._cross_compile(),
                        str(install_path),
                        str(kernel_desc.version),
                    ),
                    warn=True,
                )

                if dtb_install_result.return_code != 0:
                    self.logger.warning(
                        "Could not install kernel dtbs this command is only available for newer kernels"
                    )

                self.context.run(
                    "rm -f {}".format(
                        str(
                            install_path
                            / "lib"
                            / "modules"
                            / kernel_desc.version
                            / "build"
                        )
                    )
                )

                header_install_result = self.context.run(
                    "make headers_install ARCH={0} CROSS_COMPILE={1} INSTALL_HDR_PATH={2}".format(
                        self._arch(),
                        self._cross_compile(),
                        str(
                            install_path
                            / "lib"
                            / "modules"
                            / kernel_desc.version
                            / "build"
                        ),
                    ),
                    warn=True,
                )
                if header_install_result.return_code != 0:
                    self.logger.warning("Could not install kernel headers")

                self.context.run(
                    "make modules_install ARCH={0} CROSS_COMPILE={1} INSTALL_MOD_PATH={2}".format(
                        self._arch(), self._cross_compile(), str(install_path)
                    )
                )

            kernel_image = build_path / kernel_desc.image.build_path
            kernel_dest = (
                install_path / kernel_desc.image.deploy_path.relative_to("/")
            )

            kernel_dest.parent.mkdir(parents=True, exist_ok=True)
            self.context.run(
                "cp {0} {1}".format(str(kernel_image), str(kernel_dest))
            )

            if kernel_desc.uboot:
                build_ubimage(
                    self.context,
                    kernel_desc.uboot,
                    self._arch(),
                    build_path,
                    boot_path,
                    kernel_image,
                )

    def install(self):
        """Install kernel locally and save build directory snapshot
        """
        kernel_desc = self._kernel_desc()
        kernel_data = self._kernel_data()
        with self.context.cd(str(self.builddir)):
            kernel_dir = kernel_data.shared_data_dir
            with self.context.cd("install"):
                kernel_package = kernel_data.deploy_package_name

                self.context.run("tar czf {0} boot lib".format(kernel_package))

            kernel_top_dir = kernel_desc.kernel_srcdir.parts[0]
            kernel_build_cache = kernel_data.build_cache_name

            self.context.run(
                "tar cJf  {} {}".format(kernel_build_cache, kernel_top_dir)
            )
            self.context.run(
                "cp {} {}".format(
                    kernel_build_cache, kernel_data.build_cache_path
                )
            )

    def deploy(self):
        logging.warn("Deployment for kernels is currently not provided")
