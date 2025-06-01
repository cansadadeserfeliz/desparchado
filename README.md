# Desparchado

[![codecov](https://codecov.io/gh/cansadadeserfeliz/desparchado/branch/development/graph/badge.svg?token=JV4QDZM69Z)](https://codecov.io/gh/cansadadeserfeliz/desparchado)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Codefactor](https://www.codefactor.io/repository/github/cansadadeserfeliz/desparchado/badge?style=social)](https://www.codefactor.io/repository/github/cansadadeserfeliz/desparchado)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/feeb0eb96f654c0bbad5d0418bf70ce3)](https://app.codacy.com/gh/cansadadeserfeliz/desparchado/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![CircleCI](https://dl.circleci.com/status-badge/img/circleci/NvxPLoiXoV6rkfeDDm6qpV/XwPU1X1KYXxadqaawbZEQD/tree/development.svg?style=shield)](https://dl.circleci.com/status-badge/redirect/circleci/NvxPLoiXoV6rkfeDDm6qpV/XwPU1X1KYXxadqaawbZEQD/tree/development)


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

---

![Pony powered](http://media.djangopony.com/img/small/badge.png)
[![DigitalOcean Referral Badge](https://web-platforms.sfo2.cdn.digitaloceanspaces.com/WWW/Badge%201.svg)](https://www.digitalocean.com/?refcode=442bff99d207&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge)
