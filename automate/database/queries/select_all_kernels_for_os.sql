-- get all kernels for all board+os
select 
    ok.description as description,
    ok.version as version,
    ok.command_line as command_line,
    ok.kernel_source as kernel_source,
    ok.kernel_srcdir as kernel_srcdir,
    ok.kernel_config as kernel_config,
    ok.uboot_loadaddr as uboot_loadaddr,
    ok.uboot_image_name as uboot_image_name,
    ok.uboot_dtb_image as uboot_dtb_image,
    ok.image_deploy_path as image_deploy_path,
    ok.image_build_path as image_build_path,
    ok.is_default as is_default
from os_kernels as ok
where ok.board_os_id = {{ board_id | sqlsafe }} 
