from django.db import models

class StockPrice(models.Model):
    stock = models.CharField(max_length=15)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    last_update = models.DateTimeField(auto_now=True)
