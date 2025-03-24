# Desparchado

![Pony powered](http://media.djangopony.com/img/small/badge.png)

[![Coverage Status](https://codecov.io/gh/cansadadeserfeliz/desparchado/branch/main/graphs/badge.svg?branch=main)](https://codecov.io/github/cansadadeserfeliz/desparchado?branch=main)
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

Create migrations (example for `events` app):

    export PYTHONPATH="/app:$PYTHONPATH"
    django-admin makemigrations events

### Run the tests

    pytest


