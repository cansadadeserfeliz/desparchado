# Generated by Django 5.1.9 on 2025-06-03 00:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0033_auto_20250602_1900"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="event",
            name="event_type",
        ),
        migrations.RemoveField(
            model_name="event",
            name="topic",
        ),
    ]
