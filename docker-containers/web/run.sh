#!/bin/sh

chown -R root:root /root/.cache/pip

cd /app
pip install -r requirements.txt

while true; do
    date
    sleep 60
done
