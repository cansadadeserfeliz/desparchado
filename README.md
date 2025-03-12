# Desparchado

[![Coverage Status](https://codecov.io/gh/cansadadeserfeliz/desparchado/branch/main/graphs/badge.svg?branch=main)](https://codecov.io/github/cansadadeserfeliz/desparchado?branch=main)
[![Donate to this project using Patreon](https://img.shields.io/badge/patreon-donate-yellow.svg)](https://www.patreon.com/desparchado)
[![Codefactor](https://www.codefactor.io/repository/github/cansadadeserfeliz/desparchado/badge?style=social)](https://www.codefactor.io/repository/github/cansadadeserfeliz/desparchado)

## Development

### Setup

Start containers for Django application and PostgreSQL database:

    docker-compose build
    docker-compose up

First, open a shell for Django application:

    sudo docker exec -it desparchado-web-1 bash

Create `.env` file with environment variables, for example:

    DJANGO_SECRET_KEY='secret'
    DATABASE_NAME='desparchado_dev'
    DATABASE_USER='desparchado_dev'
    DATABASE_PASSWORD='secret'
    DATABASE_HOST='db'
    DATABASE_PORT=5432

Install static files:

    bower install

Collect static files (optional):

    python manage.py collectstatic

Run the application webserver:

    python manage.py runserver 0.0.0.0:5000

Then open http://localhost:5000/ in your browser.

Run Django shell:

    python manage.py shell

Create migrations (example for `history` app):

    export PYTHONPATH="/app:$PYTHONPATH"
    django-admin makemigrations history

### Run the tests

    pytest

## Installation

    $ sudo apt-get install gettext

    $ sudo apt-get update
    $ sudo apt-get install nodejs
    $ sudo apt-get install npm

    $ npm install -g bower
    $ npm install -g yuglify

    # Install SASS
    $ sudo apt-get install rubygems
    $ sudo su -c "gem install sass"

    # Create database
    $ createdb desparchado
    $ psql desparchado
    desparchado=# CREATE EXTENSION postgis;

    # Create virtualenv
    $ mkvirtualenv desparchado -p python3

    $ pip install uwsgi

## Deployment

    $ cd projectdir
    $ source scripts/deploy.sh

