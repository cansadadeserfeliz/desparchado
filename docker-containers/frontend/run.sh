#!/bin/sh
set -ex

echo "Running front-end container..."

npm install

npm run build
npm run start
