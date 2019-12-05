# Hello World!

Simple demonstration of bash usage. 
cross compiles for a board given default flags. Copies the binary to 
the board and executes it returning the result on the commandline.

Example with loglevel WARNING:

    $ ./run.sh
    Hello World!

Example with loglevel INFO:

    $ ./run.sh
    Compiling hello.c with compiler aarch64-gcc74
    COMPILE: /afs/wsi/es/tools/arm/gcc-linaro-7.4.1-2019.02-x86_64_aarch64-linux-gnu/bin/aarch64-linux-gnu-gcc -c -o build-jetsonagx/hello.o -O2 -march=armv8.2-a --sysroot=/local/data/es-genial/boards/jetsonagx/sysroot hello.c
    LINK: /afs/wsi/es/tools/arm/gcc-linaro-7.4.1-2019.02-x86_64_aarch64-linux-gnu/bin/aarch64-linux-gnu-gcc -o build-jetsonagx/hello -march=armv8.2-a --sysroot=/local/data/es-genial/boards/jetsonagx/sysroot build-jetsonagx/hello.o
    Connected (version 2.0, client OpenSSH_7.6p1)
    Authentication (publickey) successful!
    [chan 1] Opened sftp connection (server version 3)
    Connected (version 2.0, client OpenSSH_7.6p1)
    Authentication (publickey) successful!
    Hello World!
