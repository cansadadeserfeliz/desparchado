#!/bin/sh

set -e
set -x

cd /app
export PYTHONPATH="/app:$PYTHONPATH"

python manage.py migrate
python manage.py collectstatic --no-input

django-admin compilemessages
