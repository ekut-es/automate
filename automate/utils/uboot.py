from pathlib import Path
from string import Template

from ..model.board import UBootModel

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
                        compression = "${image_compression}";
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
                        compression = "${dtb_compression}";
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


def build_ubimage(
    c,
    uboot_desc: UBootModel,
    arch: str,
    build_path: Path,
    boot_path: Path,
    kernel_image: Path,
) -> None:
    """ Build a U-Boot image file  for kernel deployment

    # Arguments
    c: AutomateContext to run commands on
    uboot_desc: UBootModel describing image configuration
    build_path: Path of kernel Build directory
    boot_path: path of built ubimage (usually install/boot inside kernel build directory)
    kernel_image: path to kernel_image file that should be packaged inside builddir
    """
    loadaddr = uboot_desc.loadaddr
    image_name = uboot_desc.image_name
    dtb_image = uboot_desc.dtb_image
    image_compression = uboot_desc.image_compression
    dtb_compression = uboot_desc.dtb_compression

    result = FIT_TEMPLATE.safe_substitute(
        {
            "loadaddr": loadaddr,
            "image_name": str(image_name),
            "dtb_image": str(dtb_image),
            "arch": arch,
            "kernel_image": str(kernel_image),
            "image_compression": str(image_compression),
            "dtb_compression": str(dtb_compression),
        }
    )

    fit_path = build_path / "fit_image.its"
    image_path = boot_path / image_name

    with fit_path.open("w") as f:
        f.write(result)

    with c.cd(str(build_path)):
        c.run("mkimage -f {0} {1}".format(str(fit_path), str(image_path)))
