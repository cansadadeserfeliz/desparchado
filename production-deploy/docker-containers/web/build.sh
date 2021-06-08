#!/bin/sh

set -e
set -x

cd /app
python manage.py migrate
python manage.py collectstatic --no-input

export PYTHONPATH="/app:$PYTHONPATH"
django-admin compilemessages
