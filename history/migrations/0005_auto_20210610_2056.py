# Generated by Django 3.1.10 on 2021-06-11 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0004_auto_20210610_1157'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'verbose_name': 'Grupo histórico', 'verbose_name_plural': 'Grupos históricos'},
        ),
        migrations.AddField(
            model_name='historicalfigure',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='Descripción'),
        ),
    ]
