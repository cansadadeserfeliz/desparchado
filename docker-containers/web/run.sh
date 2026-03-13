#!/bin/sh
set -e
set -x

chown -R root:root /root/.cache/pip

cd /app
pip install --require-hashes -r requirements-dev.txt

python manage.py migrate
python manage.py runserver 0.0.0.0:8000
