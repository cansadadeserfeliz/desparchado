FROM postgis/postgis:13-3.1-alpine

# these are the postgres superuser credentials, they are NOT the credentials
# used by the web app. see init_dbs.sh for those
ENV POSTGRES_PASSWORD="secret"
ENV POSTGRES_USER="postgres"

COPY init_dbs.sh /docker-entrypoint-initdb.d
RUN chmod +x /docker-entrypoint-initdb.d/init_dbs.sh
