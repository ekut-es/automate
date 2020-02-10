# Setup

## Installation of Ubuntu 19.10

  Follow https://ubuntu.com/download/raspberry-pi
  
## Installation of perf

  Just sudo apt-get install linux-tools -y
  
## Kernel:

   Is built from: https://github.com/raspberrypi/linux branch rpi-5.3.y

   Deployment:
   
     tar xvzf kernel-default.tar.gz
     cp -r boot /
	 cp -r lib/modules /lib/
	 cp -r lib/firmware /lib/

   To update the initramfs:
   
   1. Edit /etc/initramfs-tools/initramfs.conf and change MODULES= to dep
   
        MODULES=dep
   
   2. Rebuild initramfs
   
        sudo update-initramfs -c -k 5.3.18 -v
  
	 
   To make the kernel the default:
   
	  sudo cp /boot/vmlinuz-5.3.18 /boot/firmware/vmlinuz
	  sudo cp /boot/initrd.img-5.3.18 /boot/firmware/initrd.img
	  sudo cp /boot/dtbs/5.3.18/bcm2711-rpi-4-b.dtb /boot/firmware/bcm2711-rpi-4-b.dtb
	  
   Then reboot and test
   
   
## ARM Trusted firmware

To support kexec and jailhouse an ARM Trusted Firmware must be built.

Build steps are as follows:

    git clone https://github.com/ARM-software/arm-trusted-firmware.git
    cd arm-trusted-firmware
	make CROSS_COMPILE=/afs/wsi/es/tools/arm/gcc-linaro-7.4.1-2019.02-x86_64_aarch64-linux-gnu/bin/aarch64-linux-gnu- PLAT=rpi4 DEBUG=1
	
Then copy 'build/rpi4/debug/bl31.bin' to the boards /boot/firmware directory and
edit /boot/firmware/config.txt to include the following lines in  [all] section.

    arm_64bit=1
    device_tree_address=0x03000000
    armstub=bl31.bin
    enable_gic=1
	enable_uart=1


After successful installation the BL31 messages should apear on serial console:


    NOTICE:  BL31: v2.2(debug):v2.2-614-gfa764c8
    NOTICE:  BL31: Built : 17:41:14, Feb 10 2020
    INFO:    Changed device tree to advertise PSCI.
    INFO:    ARM GICv2 driver initialized
    INFO:    BL31: Initializing runtime services                   
	INFO:    BL31: cortex_a72: CPU workaround for 859971 was applied
	INFO:    BL31: cortex_a72: CPU workaround for cve_2017_5715 was applied
	INFO:    BL31: cortex_a72: CPU workaround for cve_2018_3639 was applied
	INFO:    BL31: Preparing for EL3 exit to normal world


For jailhouse the patches mentioned in https://github.com/siemens/jailhouse-images/blob/7c6d0ddb2763ef38a019b565568b8e9b59ca48c8/recipes-bsp/arm-trusted-firmware/files/0001-rpi3-4-Add-support-for-offlining-CPUs.patch seem no longer necessary when using the current master of arm trusted firmware. 
