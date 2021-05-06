# Generated by Django 3.1.4 on 2020-12-08 14:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0025_auto_20200229_1814'),
        ('users', '0004_badge_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbadge',
            name='badge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_relation', to='users.badge'),
        ),
        migrations.AlterField(
            model_name='userbadge',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='badges', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='usereventrelation',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_relation', to='events.event'),
        ),
        migrations.AlterField(
            model_name='usereventrelation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='events', to=settings.AUTH_USER_MODEL),
        ),
    ]