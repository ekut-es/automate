# Commandline Interface

The commandline interface is used for interactive and scripted interaction 
with the boards. It uses the entry point automate. 


    Usage: automate [--core-opts] <subcommand> [--subcommand-opts] ...
     
    Core options:
     
      -d, --debug                        Enable debug output.
      -l [STRING], --list[=STRING]       List available tasks, optionally limited to a namespace.
      -V, --version                      Show version and exit.

Actual tasks are run as subcommands of automate.

# _automate list_

List available boards and compilers.

    Usage: automate [--core-opts] list [--options] [other tasks here ...]
     
    Docstring:
      List available boards and compilers
     
      -b/--boards: only list boards
      -c/--compilers: only list compilers

Example: 

    $ automate list 
    Boards:
    ID          Machine       Cores  OS      Connections    Default Compiler
    ----------  ----------  -------  ------  -------------  ------------------
    jetsonagx   jetsonagx         8  ubuntu  ssh            aarch64-gcc74
    zynqberry   zynqberry         2  debian  ssh            aarch32hf-gcc74
    jetsontx2   jetsontx2         6  ubuntu  ssh,uart       aarch64-gcc74
     
    Compiler:
    ID               Toolchain    Version    Machines      Multiarch
    ---------------  -----------  ---------  ------------  -----------
    aarch32hf-gcc74  gcc          7.4.1      arm           yes
    aarch32hf-gcc82  gcc          8.2.1      arm           no
    aarch32-gcc82    gcc          8.2.1      arm           no
    aarch64-gcc55    gcc          5.5.0      aarch64       yes
    aarch64-gcc82    gcc          8.2.1      aarch64       no
    aarch64-gcc65    gcc          6.5.0      aarch64       yes
    aarch64-gcc74    gcc          7.4.1      aarch64       yes
    clang-70         llvm         7.0.1      aarch64, arm  yes
    clang-80         llvm         8.0.1      aarch64, arm  yes
    clang-90         llvm         9.0.0      aarch64, arm  yes


# Board Interaction

Board interaction commands are defined in namespace _board_.

## _automate board.board-ids_

List available board ids. Useful for iterating boards in shell scripts. 

    Usage: automate [--core-opts] board.board-ids [--options] [other tasks here ...]
     
    Docstring:
      returns list of board_ids suitable for usage in shell scripts
     
      -f/--filter: filter expression for boards
     
              Filter expression is prepended with 'lambda board:  ' and then evaluated as a python function
              board is an object of class Board, only returns board_ids if filter expression is true
     
              Examples:
     
              board.machine == 'zynqberry' to only run on zynqberry boards
     
              board.trylock() to only iterate over boards that are currently 
			  unlocked, and lock the boards while iterating


Examples: 

List all available board ids:

    $automate board.board-ids
    jetsonagx
    zynqberry
    jetsontx2


List only boards with gnueabhif environment (32Bit ARM with floating point):

    $automate board.board-ids --filter 'board.os.triple.environment.value == gnueabihf'
	zynqberry


## _automate board.get_

Get files from board. 

    Usage: automate [--core-opts] board.get [--options] [other tasks here ...]
     
    Docstring:
      Get file from board
     
      -b/--board: target board id
      -r/--remote: remote file path
      -l/--local:  local folder or filename (default is current working directory)

Examples:

     automate board.get zynqberry /proc/cpuinfo
	 

## _automate board.kexec_

    Usage: automate [--core-opts] board.kexec [--options] [other tasks here ...]
     
    Docstring:
      Start the Linux kernel using kexec
     
      -b/--board: target board id
      -k/--kernel-id: target kernel id
      -a/--append: Append the given string to the commandline
      -w/--wait: wait until board is reachable via ssh again

## _automate_ board.lock


    Usage: automate [--core-opts] board.lock [--options] [other tasks here ...]
     
    Docstring:
      Lock board
     
      -b/--board: target board id
      -t/--timeout: timeout for the lock

## _automate_ board.put_

    Usage: automate [--core-opts] board.put [--options] [other tasks here ...]
     
    Docstring:
      Put file on the board
     
      -b/--board: target board id
      -f/--file: local file
      -r/--remote: remote file path (default is board specific rundir)

## _automate board.reboot_

     Usage: automate [--core-opts] board.reboot [--options] [other tasks here ...]

     Docstring:
       Reboot  board
      
       -b/--board: target board id
       -w/--wait block until the board is reachable via ssh again

## _automate board.reset_


    Usage: automate [--core-opts] board.reset [--options] [other tasks here ...]
     
    Docstring:
      Hard reset board
     
      -b/--board: target board id
      -w/--wait: block until the board is reachable again

## _automate board.rsync-to_

     Usage: automate [--core-opts] board.rsync-to [--options] [other tasks here ...]

     Docstring:
       rsync a folder to the target board by default the 
      
      
       -b/--board: target board id
       -s/--source: source folder/file
       -t/--target: target folder/file default is configured rundir on the board
       -d/--delete: delete files from target that do not exist in the source 

## _automate board.run_

    Usage: automate [--core-opts] board.run [--options] [other tasks here ...]
     
    Docstring:
      Run command remotely
     
      -b/--board: target board id
      -c/--command: command to run
      --cwd: working directory of the command (default is rundir of board)

## automate board.shell

    Usage: automate [--core-opts] board.shell [--options] [other tasks here ...]
     
    Docstring:
      Start a remote shell 
     
      -b/--board: target board id
     
    Options:
      -b STRING, --board=STRING


## automate board.unlock

    Usage: automate [--core-opts] board.unlock [--options] [other tasks here ...]
     
    Docstring:
      Unlock board
     
      -b/--board: target board id 
     
    Options:
      -b STRING, --board=STRING

# Builders

Software for boards can be built using a standard buildsystem. All buildsystem 
follow the sequence.

1. _automate $buildsystem.configure_: to configure the build
2. _automate $buildsystem.build_: to build software
3. _automate $buildsystem.install_: to install built software in a defined directory on the host system
4. _automate $buildsystem.deploy_: to copy the built software to the board

We currently have support for the following Buildsystems available: 

- _cmake_: for cmake based software builds
- _make_: for Makefile based software builds
- _kernel_: to build linux kernels using the kbuild/make base build system



# Administration tasks

Some common administration task are automated in namespace 'admin'

## _automate admin.add-users_

Adds all users ssh keys from 'metadata/users.yml' to all boards and gateways.

## _automate admin.add-board_

Adds a board to the metadata directory. This command connects to the target board 
and tries to extract the metadata automatically. As this command is not able
to extract all information 100% reliably. After extraction an interactive 
wizard is used for review of the extracted board data.

Some board data (especially os.kernel) is not generated automatically. So 
some features especially kernel building and kexec will not work with
the automatically generated board descriptions. 

    Usage: automate [--core-opts] admin.add-board [--options] [other tasks here ...]
     
    Docstring:
      Add a new board to test rack
     
      # Arguments
      --user: username on board
      --host: hostname or ip address of board
      --port: port of ssh deamon on board (optional default: 22)
      --gw-host: hostname of gateway (optional if omitted not gateway is configured)
      --gw-user: username on gateway (optional if omitted use --user)
      --gw-port: port of ssh on gateway (optional default: 22)

## _automate admin.safe-rootfs_

Safe a filesystem image of the root filesystem of a board.

Filesystem images are saved in in the path given by attribute os.rootfs of a boards metadata description. Usually the path is:  ${boardroot}/${board_name}/${board_name}.img 

*Attention:* The rootfs images are taken from the running boards, using 
a forceful readonly remount of the rootfs before taking the dump. In some cases this  might lead to a corrupted state of the filesystem dump.

    Usage: automate [--core-opts] admin.safe-rootfs [--options] 
     
    Docstring:
      Safe rootfs image of board
     
      -b/--board: target board name


## automate _admin.build-sysroot_

Convert the dumped root filesystem to a sysroot for building. Sysroots 
are not necessary for simple builds, but allow usage of libraries installed
from the boards package managers. Especially for C++ usage of sysroots 
is strongly encouraged, if libstdcxx is linked dynamically as otherwise
mismatches between the libstdcxx used for linkage and during runtime will lead
to dynamic linker errors for most programs. 

Sysroots are used by default by the builders, if they exist. 

    Usage: automate [--core-opts] admin.build-sysroot [--options]
     
    Docstring:
      Build compiler sysroot for board
     
      -b/--board: target board id



# Examples 

Examples for commandline usage can be found in _examples/shell_ folder of the project. 
