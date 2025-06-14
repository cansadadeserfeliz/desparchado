# Generated by Django 3.1.10 on 2021-06-10 16:57

import uuid

import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('history', '0003_auto_20210610_1129'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
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
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ('title', models.CharField(max_length=500, verbose_name='Título')),
                ('description', models.TextField(verbose_name='Descripción')),
                (
                    'image',
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to='history/groups',
                        verbose_name='Imagen',
                    ),
                ),
                (
                    'image_source_url',
                    models.URLField(
                        blank=True,
                        null=True,
                        verbose_name='Enlace a la fuente de la imagen',
                    ),
                ),
                (
                    'admin_comments',
                    models.TextField(
                        blank=True,
                        default='',
                        verbose_name='Comentarios de los administradores',
                    ),
                ),
                (
                    'created_by',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name='created_groups',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Creado por',
                    ),
                ),
                (
                    'members',
                    models.ManyToManyField(
                        blank=True, related_name='groups', to='history.HistoricalFigure'
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='post',
            name='published_in_groups',
            field=models.ManyToManyField(
                blank=True, related_name='posts', to='history.Group'
            ),
        ),
    ]
