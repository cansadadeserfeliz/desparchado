#!/bin/sh
set -ex

cd /app

npm install

npm run build
npm run build-storybook
