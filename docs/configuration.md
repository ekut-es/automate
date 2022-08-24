# Configuration Options

Configuration is saved in ~/.automate.yml .

It has the following sections.

## automate

metadata: Location of metadata .yml files 
metadata_url: Url of git repository containing the central metdata repository (ignored if metdata folder exists and is not a git repository)
metadata_ref: Git branch or tag of metadata (ignored if metadata folder exists and is not a git repository)
identity: (Optional) Path of ssh private key to use
toolroot: installation of tools
boardroot: Location of saved board data (Kernel SOurces, Kernel Buildds, Device Trees)
database: Database Configuration
forwards: List of port forwardings

### database 

host: host of database server
port: port of database server
db: name of database to use
user: username for database server
password: password for database server

### forwards

host: remote host for forwards
user: username for remote host
local_port: local port to forwardings
remote_port: remote_port to forward


## logging

level: loglevel for system one of ERROR, WARNING, INFO, DEBUG


# Example Configuration

An example configuration file might be:

    automate:
      metadata: /local/data/der_schrank/metadata
      identity: ~/.ssh/id_rsa
      toolroot: /afs/wsi/es/tools/
      boardroot: /nfs/es-genial/schrank/boards/
     
      
      database:
        host: localhost
        port: 5433
        db: der_schrank
        user: der_schrank
        password: der_schrank
      
      forwards:
        -
          host: chichi.informatik.uni-tuebingen.de
          user: gerum
          local_port: 5433
          remote_port: 5433
        
    logging:
      level: ERROR
