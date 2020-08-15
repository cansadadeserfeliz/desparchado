# Desparchado

[![Join the chat at https://gitter.im/vero4karu/desparchado](https://badges.gitter.im/vero4karu/desparchado.svg)](https://gitter.im/desparchado)

[![Coverage Status](https://coveralls.io/repos/github/vero4karu/desparchado/badge.svg?branch=master)](https://coveralls.io/github/vero4karu/desparchado?branch=master)
[![Build Status](https://travis-ci.org/vero4karu/desparchado.svg?branch=master)](https://travis-ci.org/vero4karu/desparchado)

<span class="badge-patreon"><a href="https://www.patreon.com/desparchado" title="Donate to this project using Patreon"><img src="https://img.shields.io/badge/patreon-donate-yellow.svg" alt="Patreon donate button" /></a></span>

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
