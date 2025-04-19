# Desparchado

![Pony powered](http://media.djangopony.com/img/small/badge.png)

[![Coverage Status](https://codecov.io/gh/cansadadeserfeliz/desparchado/branch/main/graphs/badge.svg?branch=main)](https://codecov.io/github/cansadadeserfeliz/desparchado?branch=main)
[![Codefactor](https://www.codefactor.io/repository/github/cansadadeserfeliz/desparchado/badge?style=social)](https://www.codefactor.io/repository/github/cansadadeserfeliz/desparchado)

## Development

### Setup

The application runs locally using three containers defined in `docker-compose`:

- `db` — PostgreSQL database container
- `web` — Django web application
- `frontend` — Front‑end development environment using Vite

First, create a `.env` file with the following environment variables, which will be used by the `web` container:

```bash
DJANGO_SECRET_KEY='secret'
DATABASE_NAME='desparchado_dev'
DATABASE_USER='desparchado_dev'
DATABASE_PASSWORD='secret'
DATABASE_HOST='db'
DATABASE_PORT=5432

S3_ACCESS_KEY_ID='secret'
S3_SECRET_ACCESS_KEY='secret'

AWS_SES_ACCESS_KEY_ID='secret'
AWS_SES_SECRET_ACCESS_KEY='secret'

SENTRY_CONFIG_DNS='secret'
SENTRY_ENVIRONMENT='development'
```

To build the container images, run: `make build`.

And to start them: `make up`.

Once everything is up and running, open your browser and visit [http://localhost:8000/](http://localhost:8000/) to access the application.
