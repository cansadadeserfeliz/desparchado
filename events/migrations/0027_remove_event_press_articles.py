# Generated by Django 4.2.11 on 2025-03-07 22:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0026_alter_speaker_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='press_articles',
        ),
    ]
