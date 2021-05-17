#!/bin/bash

set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
create user desparchado_dev password 'secret';
create database desparchado_dev owner desparchado_dev;
create database desparchado_test owner desparchado_dev;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname desparchado_dev <<-EOSQL
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname desparchado_test <<-EOSQL
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
EOSQL