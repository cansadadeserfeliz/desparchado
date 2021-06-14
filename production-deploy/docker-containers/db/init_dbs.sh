#!/bin/bash

set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
create user desparchado_prod password 'secret';
create database desparchado_prod owner desparchado_prod;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname desparchado_prod <<-EOSQL
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
EOSQL
