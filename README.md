# Desparchado

[![Build Status](https://travis-ci.com/cansadadeserfeliz/desparchado.svg?branch=master)](https://travis-ci.com/cansadadeserfeliz/desparchado)
[![Coverage Status](https://codecov.io/gh/cansadadeserfeliz/desparchado/branch/master/graphs/badge.svg?branch=master)](https://codecov.io/github/cansadadeserfeliz/desparchado?branch=master)
[![Donate to this project using Patreon](https://img.shields.io/badge/patreon-donate-yellow.svg)](https://www.patreon.com/desparchado)
[![Codefactor](https://www.codefactor.io/repository/github/cansadadeserfeliz/desparchado/badge?style=social)](https://www.codefactor.io/repository/github/cansadadeserfeliz/desparchado)


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

## Issues

https://tree.taiga.io/project/vero4ka-desparchado/kanban
