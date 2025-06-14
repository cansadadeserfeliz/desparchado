# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-01-09 00:25
from __future__ import unicode_literals

import django.contrib.postgres.fields
import django.core.validators
import django.utils.timezone
import model_utils.fields
from django.db import migrations, models

import games.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='HuntingOfSnarkGame',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'created',
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='created',
                    ),
                ),
                (
                    'modified',
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='modified',
                    ),
                ),
                (
                    'token',
                    models.CharField(
                        default=games.models.generate_token, max_length=255, unique=True
                    ),
                ),
                (
                    'player_name',
                    models.CharField(
                        blank=True, max_length=255, verbose_name='Juego para'
                    ),
                ),
                (
                    'total_points',
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(50),
                        ],
                        verbose_name='Cantidad de puntos',
                    ),
                ),
                (
                    'criteria_ids',
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.IntegerField(), size=None
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
