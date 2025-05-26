#!/bin/bash

set -e
set -x

cd /app
export PYTHONPATH="/app:$PYTHONPATH"

python manage.py migrate
python manage.py collectstatic --no-input

# Copy files that are not referenced correctly by django-vite
mkdir -p /app/static/assets/
cp /app/static/dist/assets/* /app/static/assets/

django-admin compilemessages
