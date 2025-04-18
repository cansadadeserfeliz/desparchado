#!/bin/sh
set -ex

npm update -g npm
npm install

npm run build
