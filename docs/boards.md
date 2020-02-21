# Board Setup

To add a new board run:

    automate admin.add-board --user <username on board> --host <hostname or ip address of board> \
	    --gw-user <username on test rack gateway> --gw-host <hostname of gateway>
		
Optionally, but recommended:

    automate 

## Installed Tools

Boards are required to have the following tools installed:
     
 1. ssh
 2. rsync
 3. netcat (nc)
 4. perf
 
## Sudo Access

Some of the tasks (admin.safe-rootfs, kernel.deploy) require root privileges. 
It is recommended to configure the board user to allow sudo without password. 

## MAC Adresses

Some of the boards (zynqberry) dynamically assign mac addresses at each reboot. 
For proper dhcp support configure a static MAC address. 

On debian based systems this can be configured in /etc/network/interfaces:

    #enable eth0 with dhcp and fixed mac address
    auto eth0
    iface eth0 inet dhcp
     	hwaddress be:bc:1c:87:3e:3f 

