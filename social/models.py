from django.db import models
from reference_data.models import Broker


"""
Model inicial, mas nao continuado.
Tem muito o que fazer.
No model, fazer uma classe que agrupe os BrokerPeriod (periodos).

No form, tem muito o que fazer...
Tb template, e views...
"""


class BrokerPeriod(models.Model):
    broker = models.ForeignKey('Broker', on_delete=models.CASCADE)
    type =  models.CharField('Tipo de corretagem', max_length=12, choices=BBT_CHOICES, default='order')

    date_from = models.DateField('De', null=True, blank=True)
    date_to = models.DateField('Até', null=True, blank=True)

    stock_brokering = models.DecimalField('Tx de corretage - à vista', max_digits=6, decimal_places=2, null=True, blank=True)
    stock_iss = models.DecimalField('ISS - à vista', max_digits=4, decimal_places=2, null=True, blank=True)

    stock_day_trade_brokerage = models.DecimalField('Tx de corretage - Daytrade', max_digits=6, decimal_places=2, null=True, blank=True)
    stock_day_trade_iss = models.DecimalField('ISS - Daytrade', max_digits=4, decimal_places=2, null=True, blank=True)

    options_trade_brokerage = models.DecimalField('Tx de corretage - Opções', max_digits=6, decimal_places=2, null=True, blank=True)
    options_trade_iss = models.DecimalField('ISS - Opções', max_digits=4, decimal_places=2, null=True, blank=True)

    # class Meta:
    #     db_table = "employee"
