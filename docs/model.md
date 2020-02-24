# Metadata Model

The necessary metadata for cross compilation and benchmark execution is 
stored in a common metadata model. 

Metadata can either be read from a local directory selected by _metadata_ in _automate.yml_ config file or in a postgres SQL database.

## Users

See _automate/model/users.py_

Users are stored as a Dict of "_Str_" -> "_UserModel_". Mapping user names 
to UserObjects. The user names can be chosen arbitrarily, but if a the systems
uses a common user database, it is recommended, that the usernames map 
to system user names. 

Each users model has the following attributes:

| Name        | Type      | Description                                                |
|-------------|-----------|------------------------------------------------------------|
| name        | str       | Full name of user                                          |
| mail        | str       | email address of user                                      |
| public_keys | List[str] | List of ssh public_keys used for authorization of the user |


## Boards

Boards are represented by an instance of _BoardModel_ see _automate/model/board.py_ .

| Name         | Type             | Description                                                                                                                        |
|--------------|------------------|---------------------------------------------------------------------------------------------------------------------------------|
| name         | str              | main unique identifier of a single board instance, chose a unique board name for each instance physical board                   |
| board        | str              | unique identifier for a board type should be the same for each instance of the same board type                                  |
| hostname     | str              | hostname of the board as defined in _/etc/hostname_ and _/etc/hosts_                                                            |
| mac_address  | str              | MAC address of the main ethernet connection of the board. For  multiple ethernet adapters chose the one connected to the gatway |
| description  | str              | Short human readable description of the board and its configuration                                                             |
| rundir       | Path             | directory on the board used for running the binaries and storing temporary results                                              |
| doc          | List             | List of [documentation links](#documentation-links)                                                                             |
| gateway      | GatewayModel     | Describes connection to the boards gateway server                                                                               |
| connections  | List             | List of ssh or uart connections usable with this board, all connections are forwarded over the boards gateway                   |
| cores        | List             | List of [core models](#cores) describing each cpu core on the board that is usable by the OS of the board                       |
| os           | OSModel          | Describes the OS Kernel and Rootfs configuration see:  [OS](#os)                                                                |
| soc          | SOCModel         | Describes the SOC used on a board see:  [SoC](#soc)                                                                             |
| power_supply | PowerSupplyModel | Describes the power supply requirements for the board see: [Power Supply](#power-supply)                                        |


## Documentation Links

Provides a link to external or internal Documentation of a board,  defined in _DocumentationLinkModel_ .

It has the following attributes:

| Name     | Type            | Description                                                                               |
|----------|-----------------|-------------------------------------------------------------------------------------------|
| title    | str             | Short description or title of the linked documentation                                    |
| location | HttpURL or Path | HttpURL to external Documentation or Path to shared file storage for shared documentation |

## Cores 

Describes a CPU-Core of the SoC. 

| Name               | Type      | Description                                                                                                     |
|--------------------|-----------|-----------------------------------------------------------------------------------------------------------------|
| num/os_id          | int       | number of the cpu in the enumeration scheme of the boards os e.g. number used for taskset -C and core isolation |
| isa                | str       | short identifier of the cores instruction set architecture                                                      |
| uarch              | str       | short identifier of the cores microarchitecture                                                                 |
| vendor/implementer | str       | name of the cpu vendor                                                                                          |
| extensions         | List[str] | List of cpu isa extensions as reported by /proc/cpuinfo                                                         |
| description        | str       | Short human readable description of the core and its main features                                              |

Currently we only describe main cores of the SoC that are under control of the OS-Scheduler, might be used to also 
describe accelerator/gpu cores in the future.

## OS

Describes the Configuration of the Operating System Kernel and RootFS.
Is defined by _OSModel_ in _automate/models/board.py_.

| Name         | Type        | Description                                                                                                                          |
|--------------|-------------|--------------------------------------------------------------------------------------------------------------------------------------|
| triple       | TripleModel | Default compiler target triple for this OS/Rootfs                                                                                    |
| distribution | str         | Name of the distribution this rootfs is based on, should correspond to _ID_ from /etc/os-release                                     |
| release      | str         | Identifier for the os release, should correspond to VERSION or VERSION_CODENAME from /etc/os-release                                 |
| description  | str         | Short human readable description of the OS                                                                                           |
| sysroot      | Path        | Path to a mirror of the relevant parts of the rootfs for cross compilation and linkage with distribution provided libraries          |
| rootfs       | Path        | Path to a snapshot of the rootfs of the system                                                                                       |
| multiarch    | bool        | this rootfs uses a [multiarch](https://wiki.debian.org/Multiarch/HOWTO) layout should probably be true only for debian based rootfes |
| kernels      | List        | List of Kernels supported by this OS Image                                                                                           |


## Kernel

The runtime and build configuration of kernels is described using _KernelModel_ from _automate/models/board.py_ .

| Name                 | Type             | Description                                                                  |
|----------------------|------------------|------------------------------------------------------------------------------|
| name                 | str              | Unique identifier for this kernel config                                     |
| description          | str              | Short human readable description of this kernel config                       |
| commandline          | str              | Default commandline of this kernel should correspond to output of _uname -r_ |
| config/kernel_config | Path             | Path to copy of the kernel build configuration file in shared data folder    |
| source/kernel_source | Path             | Path to the kernel source tarball in shared data folder                      |
| srcdir/kernel_srcdir | Path             | Relative Path to kernel source directory in extracted kernel source tarball  |
| image                | KernelImageModel |                                                                              |
| uboot                | UBootModel       |                                                                              |
| default              | bool             | This kernel is started at board power up.                                    |

### Notes

*default*: If we have not configured the default kernel for a board this might be false for all kernels. In this case the kernels are only usable using _automate board.kexec_ .

## SoC

Currently Optional: TBD

## Power Supply

Currently Optional: TBD

# Compiler Model

Metadata format for compilers has not been frozen yet: TBD

