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

    sudo docker exec -it desparchado-web-1 bash

Create `app/.env` file with environment variables, for example:

    export DJANGO_SECRET_KEY='secret'
    export DATABASE_NAME='desparchado_dev'
    export DATABASE_USER='desparchado_dev'
    export DATABASE_PASSWORD='secret'
    export DATABASE_HOST='db'
    export DATABASE_PORT=5432

Collect static files:

    python manage.py collectstatic --settings=desparchado.settings.dev

Run the application webserver:

    python manage.py runserver --settings=desparchado.settings.dev 0.0.0.0:5000

Then open http://localhost:5000/ in your browser.

Run Django shell:

    python manage.py shell --settings=desparchado.settings.dev

Create migrations (example for `history` app):

    export PYTHONPATH="/app:$PYTHONPATH"
    django-admin makemigrations history --settings=desparchado.settings.dev

### Run the tests

    make test
