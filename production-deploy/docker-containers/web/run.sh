#!/bin/sh

cd /app

uwsgi --chdir=/app \
    --module=desparchado.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=desparchado.settings.production \
    --master --pidfile=/tmp/project-master.pid \
    --socket=127.0.0.1:49152 \
    --processes=5 \                 # number of worker processes
    --uid=1000 --gid=2000 \         # if root, uwsgi can drop privileges
    --harakiri=20 \                 # respawn processes taking more than 20 seconds
    --max-requests=5000 \           # respawn processes after serving 5000 requests
    --vacuum                        # clear environment on exit
