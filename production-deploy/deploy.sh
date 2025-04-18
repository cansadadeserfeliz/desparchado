#!/bin/bash
set -e  # para salir del script si alguno de los comandos devuelve algo distinto a 0
set -x  # para imprimirme cada comando antes de ejecutarlo
cd /home/desparchado/desparchado

git checkout main
git pull

# No se va a romper si el nombre de la imagen es duplicado
docker build \
      --tag desparchado:frontend_$(date +%Y%m%d-%H%M)_$(git rev-parse --short HEAD) \
      --tag desparchado:frontend_latest \
      -f production-deploy/docker-containers/frontend/Dockerfile .

# Arrancar el contenedor de forma síncrona y corre el build de los archivos estaticos
# y los deja en /app/desparchado/static/dist dentro del contenedor
docker run --name desparchado_frontend_build \
      --mount type=bind,source=/srv/desparchado/static,target=/app/desparchado/static \
      --rm \
      desparchado:frontend_latest sh /build.sh

# No se va a romper si el nombre de la imagen es duplicado
docker build \
      --tag desparchado:web_$(date +%Y%m%d-%H%M)_$(git rev-parse --short HEAD) \
      --tag desparchado:web_latest \
      -f production-deploy/docker-containers/web/Dockerfile .

# Arrancar el contenedor de forma síncrona.
docker run --name desparchado_web_build \
      --mount type=bind,source=/srv/desparchado/static,target=/app/static \
      --mount type=bind,source=/srv/desparchado/media,target=/app/media \
      --env-file setenv.sh \
      --network container:desparchado_db \
      --rm \
      desparchado:web_latest sh /build.sh

docker stop desparchado_web
docker rm desparchado_web

docker create --name desparchado_web  \
      --mount type=bind,source=/srv/desparchado/static,target=/app/static \
      --mount type=bind,source=/srv/desparchado/media,target=/app/media \
      --env-file setenv.sh \
      --network container:desparchado_db \
      desparchado:web_latest sh /run.sh
docker start desparchado_web
