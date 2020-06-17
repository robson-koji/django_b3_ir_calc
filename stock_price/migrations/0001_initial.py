# Generated by Django 3.0.5 on 2020-05-25 23:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StockPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock', models.CharField(max_length=15, unique=True)),
                ('sector', models.CharField(blank=True, max_length=150, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('last_update', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]