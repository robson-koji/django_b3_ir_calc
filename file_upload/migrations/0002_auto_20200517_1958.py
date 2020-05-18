# Generated by Django 3.0.5 on 2020-05-17 19:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import file_upload.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('file_upload', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='document',
            name='docfile',
            field=models.FileField(upload_to=file_upload.models.get_upload_path),
        ),
    ]
