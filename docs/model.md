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

| Name        | Type      | Meaning                                                    |
|-------------|-----------|------------------------------------------------------------|
| name        | str       | Full name of user                                          |
| mail        | str       | email address of user                                      |
| public_keys | List[str] | List of ssh public_keys used for authorization of the user |


## Boards

Boards are represented by an instance of _BoardModel_ see _automate/model/board.py_ .

| Name         | Type             | Meaning                                                                                                                         |
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
describe accelerator cores in the future.

## OS

Describes the Configruation of the Operating System Kernel and RootFS.
Is defined by _OSModel_ in _automate/models/board.py_.



## SoC

## Power Supply
