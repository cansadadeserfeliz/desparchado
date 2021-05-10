#!/bin/bash

set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
create user desparchado_dev password 'secret';
create database desparchado_dev owner desparchado_dev;
create database desparchado_test owner desparchado_dev;
EOSQL