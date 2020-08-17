#!/bin/sh

DATABASE="der_schrank_test"
USER="der_schrank_test"
PASSWORD="der_schrank_test"

echo "Creating database to run postgres tests"
createdb ${DATABASE} || exit 1

echo "Creating database tables"
psql ${DATABASE} -f setup.sql || exit 1

echo "Set permissions for database ${DATABASE}"
psql ${DATABASE} -c "\
drop user if exists ${USER};\
create user ${USER} password 'md5d1b1cc38471f60d4ced326b59c9c69f5';\
grant select, insert, update, delete on all tables in schema public to ${DATABASE};\
grant select, update on all sequences in schema public to ${DATABASE};\
" || exit 1
