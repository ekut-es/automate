#!/bin/sh

DATABASE="der_schrank_test"
USER="der_schrank_test"
PASSWORD="der_schrank_test"

echo "Creating database to run postgres tests"

sudo  -u postgres psql postgres -c "create database ${DATABASE};"
sudo  -u postgres psql postgres -c "create user ${USER} with encrypted password '${PASSWORD}';"
sudo  -u postgres psql postgres -c "grant all privileges on database ${DATABASE} to ${USER};"
