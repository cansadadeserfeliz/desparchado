#!/bin/sh
set -ex

cd /app

npm install

npm run build

# Storybook is a development aid; a build failure must not block production deploy.
npm run build-storybook || echo "Storybook build failed — skipping."
