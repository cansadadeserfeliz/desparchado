# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-04-16 01:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_auto_20170418_1832'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ('event_date',), 'verbose_name': 'Evento', 'verbose_name_plural': 'Eventos'},
        ),
        migrations.AlterModelOptions(
            name='organizer',
            options={'verbose_name': 'Organizador', 'verbose_name_plural': 'Organizadores'},
        ),
        migrations.AlterModelOptions(
            name='speaker',
            options={'verbose_name': 'Presentador', 'verbose_name_plural': 'Presentadores'},
        ),
        migrations.AlterField(
            model_name='event',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_events', to=settings.AUTH_USER_MODEL, verbose_name='Creado por'),
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(default='', help_text='Puedes usar <a href="/markdown" target="_blank">Markdown</a> para dar formato al texto.', verbose_name='Descripción'),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_date',
            field=models.DateTimeField(verbose_name='Fecha del evento'),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_end_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha final'),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_source_url',
            field=models.URLField(null=True, verbose_name='Enlace a la página del evento'),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Conferencia pública'), (2, 'Debate'), (3, 'Taller'), (4, 'Recorrido'), (5, 'Encuentro'), (6, 'Obra de teatro'), (7, 'Concierto'), (8, 'Seminario'), (9, 'Exposición'), (10, 'Festival')], verbose_name='Tipo del evento'),
        ),
        migrations.AlterField(
            model_name='event',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='events', verbose_name='Imagen'),
        ),
        migrations.AlterField(
            model_name='event',
            name='image_source_url',
            field=models.URLField(blank=True, null=True, verbose_name='Créditos/atribución de la imagen'),
        ),
        migrations.AlterField(
            model_name='event',
            name='is_approved',
            field=models.BooleanField(default=True, help_text='Campo de uso exclusivo para el administrador del sitio', verbose_name='Está aprobado'),
        ),
        migrations.AlterField(
            model_name='event',
            name='is_published',
            field=models.BooleanField(default=True, help_text='Indica si el evento va a aparecer en la página', verbose_name='Está publicado'),
        ),
        migrations.AlterField(
            model_name='event',
            name='organizer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='events.Organizer', verbose_name='Organizador'),
        ),
        migrations.AlterField(
            model_name='event',
            name='place',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='places.Place', verbose_name='Lugar'),
        ),
        migrations.AlterField(
            model_name='event',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Precio'),
        ),
        migrations.AlterField(
            model_name='event',
            name='speakers',
            field=models.ManyToManyField(blank=True, null=True, related_name='events', to='events.Speaker', verbose_name='Presentadores'),
        ),
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Título'),
        ),
        migrations.AlterField(
            model_name='event',
            name='topic',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Urbanismo'), (2, 'Ciencias exactas'), (3, 'Arte'), (4, 'Emprendimiento'), (5, 'Democracia'), (6, 'Ciencias humanas'), (7, 'Idiomas'), (8, 'Literatura'), (9, 'Medioambiente'), (10, 'Medicina')], verbose_name='Tema'),
        ),
        migrations.AlterField(
            model_name='organizer',
            name='description',
            field=models.TextField(default='', verbose_name='Descripción'),
        ),
        migrations.AlterField(
            model_name='organizer',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='organizers', verbose_name='Imagen'),
        ),
        migrations.AlterField(
            model_name='organizer',
            name='image_source_url',
            field=models.URLField(blank=True, null=True, verbose_name='Enlace a la fuente de la imagen'),
        ),
        migrations.AlterField(
            model_name='organizer',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Nombre'),
        ),
        migrations.AlterField(
            model_name='organizer',
            name='website_url',
            field=models.URLField(blank=True, null=True, verbose_name='Página web'),
        ),
        migrations.AlterField(
            model_name='speaker',
            name='description',
            field=models.TextField(default='', verbose_name='Descripción'),
        ),
        migrations.AlterField(
            model_name='speaker',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='speakers', verbose_name='Imagen'),
        ),
        migrations.AlterField(
            model_name='speaker',
            name='image_source_url',
            field=models.URLField(blank=True, null=True, verbose_name='Enlace a la fuente de la imagen'),
        ),
        migrations.AlterField(
            model_name='speaker',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Nombre'),
        ),
    ]