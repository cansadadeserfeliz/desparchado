# Generated by Django 4.2.11 on 2025-03-07 23:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0006_remove_book_press_articles'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='authors',
        ),
        migrations.RemoveField(
            model_name='book',
            name='blog_posts',
        ),
        migrations.RemoveField(
            model_name='book',
            name='related_events',
        ),
        migrations.DeleteModel(
            name='Author',
        ),
        migrations.DeleteModel(
            name='Book',
        ),
    ]
