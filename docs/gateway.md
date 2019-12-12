# Gatway Configuration

This describes a simple gateway configuration assuming a 
RHEL  based system.


## Disable Network Manager for the interface

Edit the file in /etc/sysconfig/network-scripts corresponding to your device,
and disable network manager configuration by adding the following line:

    NM_CONTROLLED=no
	NETMASK=255.255.255.0
	IPADDR=192.168.1.1
	ZONE=dmz

## Enable dnsmasq

To enable dnsmasq use:
   
    yum install dnsmasq
	systemctl enable dnsmasq
    shutdown -r now
	
	
## Configure dnsmasq

Add the following in /etc/dnsmasq.d/der_schrank.conf

    listen-address=::1,127.0.0.1,192.168.1.1
	interface=enp1s0
	expand-hosts
	bogus-priv
	
	
	dhcp-range=10.42.0.10,10.42.0.150,72h
    dhcp-leasefile=/var/lib/dnsmasq/dnsmasq.leases
    dhcp-authoritative
    dhcp-option=option:ntp-server,134.2.10.50,134.2.12.2,134.2.14.2
	
	dhcp-host=jetsontx2,10.42.0.99
	dhcp-host=zynqberry,10.42.0.10

To syntax check the commandline do:
	
	dnsmasq --test
	
And apply the changes with:

    systemctl restart dnsmasq
    systemctl status dnsmasq


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
