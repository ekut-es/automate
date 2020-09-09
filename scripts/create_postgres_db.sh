#!/bin/sh

DATABASE="der_schrank_test"
USER="der_schrank_test"
PASSWORD="der_schrank_test"

MD5_HASH=$(echo -n "md5"; echo -n "${PASSWORD}${USER}" | md5sum | awk '{print $1}')
echo "Password md5 hash: $MD5_HASH"

echo "Droping database if exists"
dropdb ${DATABASE}

echo "Creating database"
createdb ${DATABASE} || exit 1

#echo "Creating database tables"
#psql ${DATABASE} -f setup.sql || exit 1

echo "Set permissions for database ${DATABASE}"
psql ${DATABASE} -c "\
drop user if exists ${USER};\
create user ${USER} password '${MD5_HASH}';\
grant select, insert, update, delete on all tables in schema public to ${DATABASE};\
grant select, update on all sequences in schema public to ${DATABASE};\
" || exit 1
