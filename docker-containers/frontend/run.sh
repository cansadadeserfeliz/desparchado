#!/bin/sh
set -ex

echo "Running front-end container..."

npm update -g npm
npm install

npm run build
npm run start
