import os
import time

from django.db import models

today  = time.strftime('%Y/%m/%d')

def get_upload_path(instance, filename):
    (file, session) = filename.split('|')
    return os.path.join('documents', session, today, file)

class Document(models.Model):
    #docfile = models.FileField(upload_to='documents/%Y/%m/%d')

    docfile = models.FileField(upload_to=get_upload_path)
