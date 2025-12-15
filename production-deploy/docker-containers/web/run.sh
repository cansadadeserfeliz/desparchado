#!/bin/sh

cd /app

# Do not increase threads, use more workers instead.
gunicorn desparchado.wsgi:application \
  --chdir /app \
  --env DJANGO_SETTINGS_MODULE=desparchado.settings.production \
  --bind 0.0.0.0:49152 \
  --workers 5 \
  --threads 1 \
  --max-requests 5000 \
  --timeout 20 \
  --user 9999 \
  --group 2000 \
  --access-logfile - \
  --error-logfile -
