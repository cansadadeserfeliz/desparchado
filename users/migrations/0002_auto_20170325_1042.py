# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-25 15:42
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usereventrelation',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_relation', to='events.Event'),
        ),
        migrations.AlterField(
            model_name='usereventrelation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to=settings.AUTH_USER_MODEL),
        ),
    ]
