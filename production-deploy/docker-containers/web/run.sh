#!/bin/sh

cd /app

uwsgi --chdir=/app \
    --module=desparchado.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=desparchado.settings.production \
    --master --pidfile=/tmp/project-master.pid \
    --http :49152 \
    --processes=5 \
    --uid=9999 --gid=2000 \
    --harakiri=20 \
    --max-requests=5000 \
    --vacuum
