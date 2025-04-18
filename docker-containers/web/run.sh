#!/bin/sh
set -e
set -x

chown -R root:root /root/.cache/pip

cd /app
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver 0.0.0.0:8000
