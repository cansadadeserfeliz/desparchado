#!/bin/sh

cd /app

uwsgi --chdir=/app \
    --module=desparchado.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=desparchado.settings.production \
    --master --pidfile=/tmp/project-master.pid \
    --socket=127.0.0.1:49152 \
    --processes=5 \
    --uid=1000 --gid=2000 \
    --harakiri=20 \
    --max-requests=5000 \
    --vacuum
