# Generated by Django 3.1.10 on 2021-06-10 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0002_auto_20210601_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='admin_comments',
            field=models.TextField(blank=True, default='', verbose_name='Comentarios de los administradores'),
        ),
        migrations.AddField(
            model_name='historicalfigure',
            name='admin_comments',
            field=models.TextField(blank=True, default='', verbose_name='Comentarios de los administradores'),
        ),
        migrations.AddField(
            model_name='post',
            name='admin_comments',
            field=models.TextField(blank=True, default='', verbose_name='Comentarios de los administradores'),
        ),
        migrations.AddField(
            model_name='post',
            name='historical_figure_mentions',
            field=models.ManyToManyField(blank=True, related_name='mentioned_in_posts', to='history.HistoricalFigure'),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_date_precision',
            field=models.CharField(choices=[('year', 'Año'), ('month', 'Mes'), ('day', 'Día'), ('hour', 'Hora'), ('minute', 'Minuto')], default='day', max_length=15),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_end_date_precision',
            field=models.CharField(blank=True, choices=[('year', 'Año'), ('month', 'Mes'), ('day', 'Día'), ('hour', 'Hora'), ('minute', 'Minuto')], default='day', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='historicalfigure',
            name='date_of_birth_precision',
            field=models.CharField(choices=[('year', 'Año'), ('month', 'Mes'), ('day', 'Día'), ('hour', 'Hora'), ('minute', 'Minuto')], default='day', max_length=15),
        ),
        migrations.AlterField(
            model_name='historicalfigure',
            name='date_of_death_precision',
            field=models.CharField(blank=True, choices=[('year', 'Año'), ('month', 'Mes'), ('day', 'Día'), ('hour', 'Hora'), ('minute', 'Minuto')], default='day', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='post_date_precision',
            field=models.CharField(blank=True, choices=[('year', 'Año'), ('month', 'Mes'), ('day', 'Día'), ('hour', 'Hora'), ('minute', 'Minuto')], default='day', max_length=15, null=True),
        ),
    ]
