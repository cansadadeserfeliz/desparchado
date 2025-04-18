#!/bin/sh
set -ex

cd /app

npm update -g npm
npm install

npm run build
