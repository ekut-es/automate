from pathlib import Path

from .. import compiler
from ..utils import untar
from ..utils.kernel import KernelConfigBuilder, KernelData
from ..utils.network import rsync
from ..utils.uboot import build_ubimage
from .builder import BaseBuilder


class KernelBuilder(BaseBuilder):
    def _kernel_desc(self, kernel_id):
        board = self.cc.board

        kernel_desc = None
        for kernel in board.os.kernels:
            if kernel.id == kernel_id:
                kernel_desc = kernel
                break

        if kernel_desc is None:
            raise Exception(
                "Could not find config with id: {} for board {}".format(
                    kernel_id, board.id
                )
            )

        return kernel_desc

    def _kernel_data(self, kernel_id):
        return KernelData(self.board, self._kernel_desc(kernel_id))

    def _arch(self):
        arch = (
            self.cc.machine.value
            if self.cc.machine.value != "aarch64"
            else "arm64"
        )
        return arch

    def _cross_compile(self):
        cross_compile = os.path.join(self.cc.bin_path, self.cc.prefix)

        return cross_compile

    def configure(self, c, kernel_id):
        self._mkbuilddir()
        kernel_desc = self._kernel_desc(kernel_id)

        with c.cd(str(self.builddir)):
            srcdir = self.builddir / kernel_desc.kernel_srcdir

            if not Path(srcdir).exists():
                c.run("cp {} .".format(kernel_desc.kernel_source))
                kernel_archive = (
                    self.builddir / Path(kernel_desc.kernel_source).name
                )
                untar(kernel_archive, self.builddir)

            with c.cd(str(srcdir)):

                c.run("cp {} .config".format(kernel_desc.kernel_config))

                c.run(
                    "make ARCH={0} CROSS_COMPILE={1} oldconfig".format(
                        self._arch(), self._cross_compile()
                    )
                )

                config_builder = KernelConfigBuilder(self.board, self.cc)
                config_fragment = srcdir / ".config_fragment"
                with config_fragment.open("w") as fragment:
                    fragment_str = config_builder.predefined_config_fragment(
                        kernel_id
                    )
                    print(fragment_str)
                    fragment.write(fragment_str)

                with c.prefix(
                    "export ARCH={0} && export CROSS_COMPILE={1}".format(
                        self._arch(), self._cross_compile()
                    )
                ):
                    c.run(
                        "./scripts/kconfig/merge_config.sh .config .config_fragment"
                    )

                c.run("cp .config {}".format(kernel_desc.kernel_config))

    def build(self, c, kernel_id):
        self._mkbuilddir()
        kernel_desc = self._kernel_desc(kernel_id)

        build_path = Path(self.builddir)
        install_path = build_path / "install"
        boot_path = install_path / "boot"
        c.run("rm -rf {}".format(install_path))

        with c.cd(str(self.builddir)):
            srcdir = kernel_desc.kernel_srcdir
            with c.cd(str(srcdir)):

                c.run(
                    "make ARCH={0} CROSS_COMPILE={1}".format(
                        self._arch(), self._cross_compile()
                    )
                )

                c.run(
                    "make modules_install ARCH={0} CROSS_COMPILE={1} INSTALL_MOD_PATH={2}".format(
                        self._arch(), self._cross_compile(), str(install_path)
                    )
                )

            kernel_image = build_path / kernel_desc.image.build_path
            kernel_dest = (
                install_path / kernel_desc.image.deploy_path.relative_to("/")
            )

            kernel_dest.parent.mkdir(parents=True, exist_ok=True)
            c.run("cp {0} {1}".format(str(kernel_image), str(kernel_dest)))

            if kernel_desc.uboot:
                build_ubimage(
                    c,
                    kernel_desc.uboot,
                    self._arch(),
                    build_path,
                    boot_path,
                    kernel_image,
                )

    def install(self, c, kernel_id):
        kernel_desc = self._kernel_desc(kernel_id)
        kernel_data = self._kernel_data(kernel_id)
        with c.cd(str(self.builddir)):
            kernel_dir = kernel_data.shared_data_dir
            with c.cd("install"):
                kernel_package = kernel_data.deploy_package_name

                c.run("tar czf {0} boot lib".format(kernel_package))
                c.run(
                    "cp {0} {1}".format(
                        kernel_package, kernel_data.build_cache_name
                    )
                )

            kernel_top_dir = kernel_desc.kernel_srcdir.parts[0]
            kernel_build_cache = kernel_data.build_cache_name

            c.run("tar cJf  {} {}".format(kernel_build_cache, kernel_top_dir))
            c.run(
                "cp {} {}".format(
                    kernel_build_cache, kernel_data.build_cache_path
                )
            )
