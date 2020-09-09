# Setup PostgreSQL Database Server 

This describes a simple gateway configuration assuming a 
RHEL/CentOS 7 based system. 
Source: [https://yallalabs.com/linux/how-to-install-postgresql-10-on-centos-7-rhel-7/](https://yallalabs.com/linux/how-to-install-postgresql-10-on-centos-7-rhel-7/)


## Add PostgreSQL 10 Repo to yum

```
sudo yum install https://download.postgresql.org/pub/repos/yum/10/redhat/rhel-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm -y`
```


## Install PostgreSQL 10 

```
sudo yum install postgresql10 postgresql10-server postgresql10-contrib postgresql10-libs -y
```


## Initialize and Start PostgreSQL Server 

```
sudo /usr/pgsql-10/bin/postgresql-10-setup initdb
sudo systemctl enable postgresql-10.service
sudo systemctl start postgresql-10.service
```


## Login into PostgreSQL Server

```
sudo su - postgres
psql
```


## Change PostgreSQL config 

In `/var/lib/pgsql/10/data/pg_hba.conf` change the following lines from
```
local   all             all                                     peer
# IPv4 local connections:
host    all             all             127.0.0.1/32            ident
# IPv6 local connections:
host    all             all             ::1/128                 ident
```
to
```
# Database administrative login by Unix domain socket
local   all             postgres                                peer
# "local" is for Unix domain socket connections only
local   all             all                                     md5
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
# # IPv6 local connections:
host    all             all             ::1/128                 md5
```
to allow password authentification

Restart PostgreSQL server:
```
sudo systemctl restart postgresql-10.service
```


## Setup Database
In the [create_postgres_db.sh](../scripts/create_postgres_db.sh) change `DATABASE`, `USER`, and `PASSWORD` and execute the script to create the automate database.
Login in as user `postgres` and run the script:
```
sudo su - postgres
./create_postgres_db.sh
```

## Connect to Database

Add `DATABASE`, `USER`, and `PASSWORD` to your `automate.yml` and if necessary activate a proper port forwarding. 

To initialize the database tables run:

```
    automate database.init
```