import logging
import os
import shutil
from pathlib import Path
from string import Template
from typing import Union

from .. import compiler
from ..utils import untar
from ..utils.kernel import KernelConfigBuilder
from ..utils.network import rsync

FIT_TEMPLATE = Template(
    r"""
/*
 * Simple U-Boot uImage source file containing a single kernel and FDT blob
 */

/dts-v1/;

/ {
	description = "Simple image with single Linux kernel and FDT blob";
	#address-cells = <1>;

	images {
		kernel {
			description = "Linux kernel";
			data = /incbin/("${kernel_image}");
			type = "kernel";
			arch = "${arch}";
			os = "linux";
			compression = "none";
			load = <${loadaddr}>;
			entry = <${loadaddr}>;
			hash-1 {
				algo = "crc32";
			};
			hash-2 {
				algo = "sha1";
			};
		};
		fdt-1 {
			description = "Flattened Device Tree blob";
			data = /incbin/("${dtb_image}");
			type = "flat_dt";
			arch = "${arch}";
			compression = "none";
			hash-1 {
				algo = "crc32";
			};
			hash-2 {
				algo = "sha1";
			};
		};
	};

	configurations {
		default = "conf-1";
		conf-1 {
			description = "Boot Linux kernel with FDT blob";
			kernel = "kernel";
			fdt = "fdt-1";
		};
	};
};
"""
)


class BaseBuilder(object):
    def __init__(
        self,
        cc: "compiler.CrossCompiler",
        builddir: Union[Path, str] = "",
        srcdir: Union[Path, str] = "",
        prefix: Union[Path, str] = "",
    ):
        self.cc = cc

        if builddir:
            self.builddir = Path(builddir)
        else:
            self.builddir = Path(cc.default_builddir)
        if srcdir:
            self.srcdir = Path(srcdir)
        else:
            self.srcdir = Path(".")

        if prefix:
            self.prefix = Path(prefix)
        else:
            self.prefix = Path(cc.board.rundir)

        self.prefix = self.prefix.absolute()
        self.srcdir = self.srcdir.absolute()
        self.builddir = self.builddir.absolute()

        self.logger = logging.getLogger(__name__)

    @property
    def board(self):
        return self.cc.board

    def configure(self, c):
        "Configure the build"

        raise NotImplementedError("Configure is not implemented")

    def build(self, c):
        "Build target code"
        raise NotImplementedError("Build is not implemented")

    def install(self, c):
        "Installs the built binaries on the board"
        raise NotImplementedError("Installation is not implemented")

    def clean(self, c):
        "Removes the builddir"
        if self.builddir != self.srcdir:
            if self.builddir.exists():
                shutil.rmtree(self.builddir)

    def _mkbuilddir(self):
        "Creates the build directory"
        self.builddir.mkdir(parents=True, exist_ok=True)


class CMakeBuilder(BaseBuilder):
    def configure(self, c, cmake_definitions=[]):
        self._mkbuilddir()

        toolchain_file_name = self.builddir / "toolchain.cmake"
        with toolchain_file_name.open("w") as toolchain_file:
            toolchain_file.write("set(CMAKE_SYSTEM_NAME Linux)\n")
            toolchain_file.write(
                "set(CMAKE_SYSTEM_PROCESSOR {})\n".format(self.cc.machine.value)
            )
            toolchain_file.write("\n")
            toolchain_file.write(
                "set(CMAKE_SYSROOT {})\n".format(self.cc.sysroot)
            )
            toolchain_file.write(
                "set(CMAKE_STAGING_PREFIX {})\n".format(
                    self.builddir / "install"
                )
            )
            toolchain_file.write("\n")
            toolchain_file.write(
                "set(CMAKE_C_COMPILER {}/{})\n".format(
                    self.cc.bin_path, self.cc.cc
                )
            )
            toolchain_file.write(
                "set(CMAKE_CXX_COMPILER {}/{})\n".format(
                    self.cc.bin_path, self.cc.cxx
                )
            )
            toolchain_file.write("\n")
            toolchain_file.write(
                "set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)\n"
            )
            toolchain_file.write(
                "set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)\n"
            )
            toolchain_file.write(
                "set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)\n"
            )
            toolchain_file.write(
                "set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)\n"
            )
            toolchain_file.write("\n")

        cache_file_name = self.builddir / "cache.cmake"
        with cache_file_name.open("w") as cache_file:
            cache_file.write("#Compiler options \n")
            cflags = self.cc.cflags
            cache_file.write(
                'set(CMAKE_C_FLAGS_DEBUG          "{} -g" CACHE STRING "")\n'.format(
                    cflags
                )
            )
            cache_file.write(
                'set(CMAKE_C_FLAGS_MINSIZEREL     "{} -DNDEBUG" CACHE STRING "")\n'.format(
                    cflags
                )
            )
            cache_file.write(
                'set(CMAKE_C_FLAGS_RELWITHDEBINFO "{} -g -DNDEBUG" CACHE STRING "")\n'.format(
                    cflags
                )
            )
            cache_file.write(
                'set(CMAKE_C_FLAGS_RELEASE        "{} -DNDEBUG" CACHE STRING "")\n'.format(
                    cflags
                )
            )
            cache_file.write("\n")

            cxxflags = self.cc.cxxflags
            cache_file.write(
                'set(CMAKE_CXX_FLAGS_DEBUG          "{} -g" CACHE STRING "")\n'.format(
                    cxxflags
                )
            )
            cache_file.write(
                'set(CMAKE_CXX_FLAGS_MINSIZEREL     "{} -DNDEBUG" CACHE STRING "")\n'.format(
                    cxxflags
                )
            )
            cache_file.write(
                'set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "{} -g -DNDEBUG" CACHE STRING "")\n'.format(
                    cxxflags
                )
            )
            cache_file.write(
                'set(CMAKE_CXX_FLAGS_RELEASE        "{} -DNDEBUG" CACHE STRING "")\n'.format(
                    cxxflags
                )
            )

        definitions = " ".join(["-D{}".format(d) for d in cmake_definitions])

        with c.cd(str(self.builddir)):
            command = "cmake -DCMAKE_BUILD_TYPE='RELWITHDEBINFO' -DCMAKE_TOOLCHAIN_FILE=toolchain.cmake -C cache.cmake {} {}".format(
                self.srcdir, definitions
            )
            self.logger.info("Running cmake: {}".format(command))
            c.run(command)

    def build(self, c):
        self._mkbuilddir()
        with c.cd(str(self.builddir)):
            c.run("cmake --build  .")

    def install(self, c, delete=False):
        with c.cd(str(self.builddir)):
            c.run("cmake  --build . --target install ")

        with self.cc.board.connect() as con:
            rsync(
                con,
                source=str(self.builddir / "install") + "/",
                target=str(self.prefix),
                delete=delete,
                rsync_opts="-l",
            )


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
        boot_path = build_path / "boot"

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
                        self._arch(), self._cross_compile(), str(build_path)
                    )
                )

            arch = self._arch()
            kernel_zimage = (
                build_path / srcdir / "arch" / arch / "boot" / "zImage"
            )
            kernel_image = (
                build_path / srcdir / "arch" / arch / "boot" / "Image"
            )
            boot_path.mkdir(exist_ok=True)
            c.run("cp {0} {1}".format(str(kernel_zimage), str(boot_path)))
            c.run("cp {0} {1}".format(str(kernel_image), str(boot_path)))

            if kernel_desc.uboot:
                loadaddr = kernel_desc.uboot.loadaddr
                image_name = kernel_desc.uboot.image_name
                dtb_image = kernel_desc.uboot.dtb_image

                result = FIT_TEMPLATE.safe_substitute(
                    {
                        "loadaddr": loadaddr,
                        "image_name": image_name,
                        "dtb_image": dtb_image,
                        "arch": arch,
                        "kernel_image": kernel_zimage,
                    }
                )

                fit_path = build_path / "fit_image.its"
                image_path = boot_path / image_name

                with fit_path.open("w") as f:
                    f.write(result)

                c.run(
                    "mkimage -f {0} {1}".format(str(fit_path), str(image_path))
                )

    def install(self, c, kernel_id):
        kernel_desc = self._kernel_desc(kernel_id)
        with c.cd(str(self.builddir)):
            srcdir = kernel_desc.kernel_srcdir
            with c.cd(str(srcdir)):

                c.run(
                    "make targz-pkg ARCH={0} CROSS_COMPILE={1}".format(
                        self._arch(), self._cross_compile()
                    )
                )


class MakefileBuilder(BaseBuilder):
    # TODO: implement Makefile Builder
    pass


class SPECBuilder(BaseBuilder):
    # TODO: implement spec Builder
    pass


class AutotoolsBuilder(BaseBuilder):
    # TODO: implement spec Builder
    pass
