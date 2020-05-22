import os
import time

from django.db import models
from django.contrib.auth.models import User

today  = time.strftime('%Y/%m/%d')

def get_upload_path(instance, filename):
    (file, session) = filename.split('|')
    return os.path.join('documents', session, today, file)

class Document(models.Model):
    #docfile = models.FileField(upload_to='documents/%Y/%m/%d')
    docfile = models.FileField(upload_to=get_upload_path)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    session_key = models.CharField(max_length=40)


from django.db.models.signals import post_save
from django.dispatch import receiver

# method for updating
@receiver(post_save, sender=Document)
def update_stock_price(sender, instance, **kwargs):
    
    import pdb; pdb.set_trace()
    instance.product.stock -= instance.amount
    instance.product.save()
