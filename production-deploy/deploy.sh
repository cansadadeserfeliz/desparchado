#!/bin/bash
set -e  # stop the script if any command fails
set -x  # print each command before running it

# Create the folder where storybook will save its static build
mkdir -p /home/desparchado/desparchado/storybook-static

cd /home/desparchado/desparchado

git checkout main
git pull

# Build the frontend image. It adds two tags:
# - one tag with date and commit hash
# - one tag called "frontend_latest"
docker build \
      --tag "desparchado:frontend_$(date +%Y%m%d-%H%M)_$(git rev-parse --short HEAD)" \
      --tag desparchado:frontend_latest \
      -f production-deploy/docker-containers/frontend/Dockerfile .

# Run the frontend build container.
# The first bind mount lets the container write the static JS/CSS build
# into the host folder /home/desparchado/desparchado/desparchado/static
# → this becomes /app/desparchado/static inside the container.
#
# The second bind mount lets the container write the storybook build
# into the host folder /srv/desparchado/storybook
# → this becomes /app/storybook-static inside the container.
docker run --name desparchado_frontend_build \
      --mount type=bind,source=/home/desparchado/desparchado/desparchado/static,target=/app/desparchado/static \
      --mount type=bind,source=/srv/desparchado/storybook,target=/app/storybook-static \
      --rm \
      desparchado:frontend_latest sh /build.sh

# Build the backend web image with two tags (date+commit and "web_latest")
docker build \
      --tag "desparchado:web_$(date +%Y%m%d-%H%M)_$(git rev-parse --short HEAD)" \
      --tag desparchado:web_latest \
      -f production-deploy/docker-containers/web/Dockerfile .

# Run the backend build container.
# It collects static files and other assets.
#
# Bind mount 1:
#   /srv/desparchado/static on host → /app/static inside container
#   The container writes collected static files into the host folder.
#
# Bind mount 2:
#   /srv/desparchado/media on host → /app/media inside container
#   This keeps user-uploaded files available to the container.
docker run --name desparchado_web_build \
      --mount type=bind,source=/srv/desparchado/static,target=/app/static \
      --mount type=bind,source=/srv/desparchado/media,target=/app/media \
      --env-file setenv.sh \
      --network container:desparchado_db \
      --rm \
      desparchado:web_latest sh /build.sh

docker stop desparchado_web
docker rm desparchado_web

# Create the final runnable container for production.
# It uses the same static and media bind mounts so the app can read
# the built assets and the uploaded files.
docker create --name desparchado_web  \
      --mount type=bind,source=/srv/desparchado/static,target=/app/static \
      --mount type=bind,source=/srv/desparchado/media,target=/app/media \
      --env-file setenv.sh \
      --network container:desparchado_db \
      desparchado:web_latest sh /run.sh
docker start desparchado_web
