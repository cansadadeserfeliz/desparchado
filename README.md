# Desparchado

[![Build Status](https://travis-ci.com/cansadadeserfeliz/desparchado.svg?branch=master)](https://travis-ci.com/cansadadeserfeliz/desparchado)
[![Coverage Status](https://codecov.io/gh/cansadadeserfeliz/desparchado/branch/master/graphs/badge.svg?branch=master)](https://codecov.io/github/cansadadeserfeliz/desparchado?branch=master)
[![Donate to this project using Patreon](https://img.shields.io/badge/patreon-donate-yellow.svg)](https://www.patreon.com/desparchado)
[![Codefactor](https://www.codefactor.io/repository/github/cansadadeserfeliz/desparchado/badge?style=social)](https://www.codefactor.io/repository/github/cansadadeserfeliz/desparchado)

## Development

### Setup

Start containers for Django application and PostgreSQL database:

    docker-compose build
    docker-compose up

First, open a shell for Django application:

    sudo docker exec -it desparchado_web_1 bash

Create `app/setenv.sh` file with environment variables, for example:

    export DJANGO_SECRET_KEY='secret'
    export DATABASE_NAME='desparchado_dev'
    export DATABASE_USER='desparchado_dev'
    export DATABASE_PASSWORD='secret'
    export DATABASE_HOST='db'
    export DATABASE_PORT=5432

Load environment variables from `app/setenv.sh`:

    cd app/
    source setenv.sh

Install static files:

    bower install

Collect static files:

    python manage.py collectstatic --settings=desparchado.settings.local

Run the application webserver:

    python manage.py runserver --settings=desparchado.settings.local 0.0.0.0:5000

Run Django shell:

    python manage.py shell --settings=desparchado.settings.local

Create migrations (example for `history` app):

    export PYTHONPATH="/app:$PYTHONPATH"
    django-admin makemigrations history --settings=desparchado.settings.local

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

