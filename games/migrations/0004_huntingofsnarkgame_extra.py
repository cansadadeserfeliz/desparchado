# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-01-19 00:51
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0003_auto_20190110_2159'),
    ]

    operations = [
        migrations.AddField(
            model_name='huntingofsnarkgame',
            name='extra',
            field=django.db.models.JSONField(default={}),
        ),
    ]
