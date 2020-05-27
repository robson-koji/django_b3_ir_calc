from django.db import models

class StockPrice(models.Model):
    stock = models.CharField(unique=True, max_length=15)
    sector = models.CharField(max_length=150, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    hour = models.CharField(max_length=30, null=True, blank=True) # Time provided by Yahoo
    last_update = models.DateTimeField(null=True, blank=True)
