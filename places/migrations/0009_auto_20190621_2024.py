# Generated by Django 2.0.13 on 2019-06-22 01:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0008_auto_20190209_1828'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='show_on_home',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='place',
            name='city',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING,
                to='places.City',
                verbose_name='Ciudad',
            ),
        ),
        migrations.AlterField(
            model_name='place',
            name='created_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING,
                to=settings.AUTH_USER_MODEL,
                verbose_name='Creado por',
            ),
        ),
    ]
