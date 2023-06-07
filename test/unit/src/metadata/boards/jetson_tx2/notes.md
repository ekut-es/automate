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

### hwloc
    
Compiled on device 
	
	./configure  --disable-opencl  CFLAGS=-I/usr/local/cuda/include LDFLAGS="-L/usr/local/cuda/lib64"
	make -j8
	sudo make install
   
### Buildroot

The Buildroot has been generated using the following command:

    rsync -arcv es@192.168.55.1:/ /local/data/buildroots/jetsontx2 --exclude=/sys --exclude=/etc --exclude=/home --exclude=/proc --exclude=/run --exclude=/lost+found --exclude=/tmp --exclude=/root
	./scripts/fix_symlinks.py /local/data/buildroots/jetsontx2
