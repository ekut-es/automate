### Manual Configurations

#### CPU Isolation

   The Carmel cores 1-7 can be isolated using using kernel parameter: isolcpus=1,2,3,4,5,6,7. CPU isolation is **not** activated by default. 
   
   To change this configuration:
   
   1. Launch the appropriate docker container 
   
        cd sdk_manager_docker/sdk_0.9.13
	    ./launch_container.sh
   
   2. Change to jetpack linux directory
   
        cd nvidia/nvidia_sdk/JetPack_4.2.1_Linux_GA_P2888/Linux_for_Tegra
   
   3. Start board in Recovery Mode
   
   4. Flash a modified device tree
   
        sudo ./flash.sh -C isolcpus=1,2,3,4,5,6,7  -k kernel-dtb jetson-xavier mmcblk0p1
		
	To change back to default configuration use:
	
	    sudo ./flash.sh  -k kernel-dtb jetson-xavier mmcblk0p1
   
   5. Restart board

### Packages installed from Source

#### POCL

   Nvidia does not officially support OpenCL on its Embedded Boards. To allow 
   the execution of OpenCL-Code Portable OpenCL 1.3 with support for GPU and CPU 
   has been installed. 

    mkdir build
    cd build
    cmake -DENABLE_CUDA=ON
    make
    sudo make install

#### perf
   
   Compiled on device
   
    git clone git://nv-tegra.nvidia.com/linux-4.9.git
	cd linux-4.9
    git checkout tegra-l4t-r32.2.0
	sudo apt-get install libelf-dev libdw-dev systemtap-sdt-dev libunwind-dev libaudit-dev libssl-dev libslang2-dev binutils-dev liblzma-dev libpcap0.8-dev
	cd tools/perf
	make LDFLAGS=-lcap-ng
	sudo make install DESTDIR=/usr
   
   
### Buildroot

The Buildroot has been generated using the following command:

    rsync -arcv es@192.168.55.1:/ /local/data/buildroots/jetsonagx --exclude=/sys --exclude=/etc --exclude=/home --exclude=/proc --exclude=/run --exclude=/lost+found --exclude=/tmp --exclude=/root
