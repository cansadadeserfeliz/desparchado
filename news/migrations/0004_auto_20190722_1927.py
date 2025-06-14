# Generated by Django 2.0.13 on 2019-07-23 00:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_pressarticle_publication_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pressarticle',
            options={
                'ordering': ('-publication_date',),
                'verbose_name': 'Press article',
                'verbose_name_plural': 'Press articles',
            },
        ),
        migrations.AddField(
            model_name='mediasource',
            name='source_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('blog', 'blog'),
                    ('booktube', 'booktube'),
                    ('podcast', 'podcast'),
                    ('magazine', 'magazine'),
                ],
                db_index=True,
                max_length=50,
                null=True,
                verbose_name='Tipo del recurso',
            ),
        ),
    ]
