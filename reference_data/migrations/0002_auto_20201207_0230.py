# Generated by Django 3.0.5 on 2020-12-07 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference_data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Indice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('indice', models.CharField(choices=[('ICON', 'Consumo'), ('IEEX', 'Energia'), ('IFNC', 'Financeiro'), ('IMOB', 'Imobiliário'), ('IMAT', 'Materiais Básicos'), ('SMLL', 'Small'), ('UTIL', 'Utilities')], default='order', max_length=12)),
            ],
        ),
        migrations.AddField(
            model_name='ativos',
            name='indice',
            field=models.ManyToManyField(to='reference_data.Indice'),
        ),
    ]
