# Generated by Django 3.0.5 on 2021-06-01 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0002_mmalert_timeframe'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mmalert',
            name='datetime',
        ),
        migrations.AlterField(
            model_name='mmalert',
            name='smm',
            field=models.IntegerField(blank=True, default=9, null=True),
        ),
    ]
