# Generated by Django 3.0.5 on 2021-05-24 02:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reference_data', '0007_cotacoes'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cotacoes',
            unique_together={('stock', 'datetime')},
        ),
    ]
