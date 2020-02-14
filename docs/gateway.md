# Gatway Configuration

This describes a simple gateway configuration assuming a 
RHEL  based system.

## Disable Network Manager for the interface

All boards are part of a network (10.42.0.0/24) administered by the gateway. The board network is connected to a dedicated network interface of the gateway. To assign a static IP address to the network interface get the name and MAC address of the network interface by executing:

    ifconfig -a

Edit or add the file in `/etc/sysconfig/network-scripts/ifcfg-IF_NAME` corresponding to your device and replace all content of the file with the following:

	TYPE=Ethernet
	DEFROUTE=no
	IPV4_FAILURE_FATAL=no
	IPV6INIT=yes
	IPV6_AUTOCONF=shared
	IPV6_DEFROUTE=yes
	IPV6_FAILURE_FATAL=no
	HWADDR=xx:xx:xx:xx:xx:xx
	ONBOOT=yes
	IPV6_ADDR_GEN_MODE=stable-privacy
	IPV6_PRIVACY=no
	PROXY_METHOD=none
	BROWSER_ONLY=no
	BOOTPROTO=shared
	NM_CONTROLLED=no
	NETMASK=255.255.255.0
	IPADDR=10.42.0.1
	ZONE=dmz


## Disable Network Manager dnsmasq

By default Network Manager runs a DNS/DHCP server. This DNS server has to be disabled by editing `/etc/NetworkManager/NetworkManager.conf`. Under section `[main]` add the following line to the config file:

	dns=none

Reboot the computer:

	shutdown -r now


## Enable dnsmasq

To enable dnsmasq use:
   
    yum install dnsmasq
	systemctl enable dnsmasq
	
	
## Configure dnsmasq

Add the following in `/etc/dnsmasq.d/derschrank.conf`

	listen-address=::1,127.0.0.1,10.42.0.1
	port=53
	interface=enp0s20u3
	domain-needed
	expand-hosts
	server=134.2.12.15
	server=134.2.12.4
	server=134.2.12.17

	dhcp-range=10.42.0.10,10.42.0.150,72h
	dhcp-leasefile=/var/lib/dnsmasq/dnsmasq.leases
	dhcp-authoritative
	dhcp-option=option:ntp-server,134.2.10.50,134.2.12.2,134.2.14.2

To syntax check the commandline do:
	
	dnsmasq --test
	
And apply the changes with:

    systemctl restart dnsmasq
    systemctl status dnsmasq

When a new board is installed and joins the network. The hostname, MAC address, and IP address can be found in: `/var/lib/dnsmasq/dnsmasq.leases`. To assign a static IP to a board add the following line to `/etc/dnsmasq.d/derschrank.conf`: 

	dhcp-host=yy:yy:yy:yy:yy:yy,boardhostname,10.42.0.YY

In order to make the locallay installed dnsmasq server the primary DNS server edit `/etc/resolv.conf` with the following line:

	nameserver 127.0.0.1
	search your.localdomain.com

## Configure NAT forwarding

     yum install firewalld
     systemctl enable firewalld
	 systemctl start firewalld
	 systemctl status firewalld

### Configure DMZ

    firewall-cmd --zone=dmz --add-service=ntp  --permanent
	firewall-cmd --zone=dmz --add-service=dhcp --permanent
	firewall-cmd --zone=dmz --add-service=dns  --permanent
	firewall-cmd --zone=dmz --add-service=http --permanent
	firewall-cmd --zone=dmz --add-service=https --permanent
	firewall-cmd --zone=dmz --remove-service=ssh --permanent
	
    firewall-cmd --reload

### Configure Public Zone

If gateway is a normal staff host you might want to enable usual stuff:

    firewall-cmd --zone=public --add-service=nfs --permanent
	firewall-cmd --zone=public --add-service=nfs3 --permanent
    firewall-cmd --zone=public --add-service=mdns --permanent
    firewall-cmd --zone=public --add-service=samba-client --permanent

    firewall-cmd --permanent --new-service=afs-client
    firewall-cmd --permanent --service=afs-client --set-description="Allows to use afs cache manager"
    firewall-cmd --permanent --service=afs-client --add-port=7001/udp
    firewall-cmd --permanent --service=afs-client --add-port=7001/tcp
    firewall-cmd --zone=public --add-service=afs-client --permanent

    firewall-cmd --zone=public --add-service=ipp --permanent
	firewall-cmd --reload


## Configure masquerading


	firewall-cmd --zone=public --add-rich-rule="rule family=ipv4 source address=10.42.0.0/24 masquerade" --permanent
	firewall-cmd --reload

FIXME: this rule is too permissive to allow untrusted users on the boards.

This would probably need direct rules  https://www.lisenet.com/2016/firewalld-rich-and-direct-rules-setup-rhel-7-server-as-a-router/

Or maybe just disable masquerading and install an ntp server on the gateway.
