#!/bin/bash

echo "Running npm install..."
npm update -g npm
npm install

#npm start

while true; do
    date
    sleep 60
done