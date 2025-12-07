FROM postgis/postgis:18-3.6-alpine

# these are the postgres superuser credentials
ENV POSTGRES_PASSWORD="secret"
ENV POSTGRES_USER="postgres"

COPY init_dbs.sh /docker-entrypoint-initdb.d
RUN chmod +x /docker-entrypoint-initdb.d/init_dbs.sh
