from django.db import models
from django.contrib.auth.models import User

# Broker Brokerage Type
TF_CHOICES = (
    ('15min','15min'),
    ('1H', '1H'),
    ('2H', '2H'),
    ('4H', '4H'),
    ('D', 'D'),
    ('W', 'W'),
)

class MmAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.CharField(max_length=12, null=True, blank=True)
    timeframe =  models.CharField(max_length=7, choices=TF_CHOICES, default='15min')
    smm = models.IntegerField(null=True, blank=True)
    emm = models.IntegerField(null=True, blank=True)
    datetime = models.DateTimeField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
            return "%s: %s SMM: %s EMM: %s" % (self.stock, self.timeframe, self.smm, self.emm)
