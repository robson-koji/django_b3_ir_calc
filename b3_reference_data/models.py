from django.db import models
from datetime import date

class Setorial(models.Model):
    """ Economy sector of the company, reference data """

    setor = models.CharField(max_length=150, help_text='Usabo para setor, subsetor e segmento')
    pai = models.ForeignKey("self", on_delete=models.CASCADE, null=True, help_text='Montar a hierarquia de setor, subsetor, segmento')

    def get_arvore_setorial(self):
        segmento = self
        if segmento.pai:
            subsetor = segmento.pai
            if subsetor.pai:
                setor = subsetor.pai
        return ("%s|%s|%s" % (setor, subsetor,segmento))

    def __str__(self):
            return self.setor

class Ativos(models.Model):
    """ Holds data for BTC, Termo, mkt value and economy sector of the company """
    ativo = models.CharField(max_length=10, null=True, blank=True)
    chave_1 = models.CharField(max_length=100, null=True, blank=True, help_text=u"Usado em algumas tabelas da B3 que relacionam os papeis por esta chave.")
    valor_mercado = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    setorial = models.ForeignKey('Setorial', on_delete=models.CASCADE)
    btc = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text=u"Soma btc de preferenciais e ordinarias")
    termo = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text=u"Soma termo de preferenciais e ordinarias")

    def get_pct_sum_btc_termo_vm(self):
        if not self.valor_mercado or not self.btc or not self.termo:
            return None
        btc_termo  = self.btc + self.termo
        get_pct_sum_btc_termo_vm = btc_termo * 100 / (self.valor_mercado * 1000)
        return get_pct_sum_btc_termo_vm

    def get_pct_btc_vm(self):
        if not self.valor_mercado or not self.btc or not self.termo:
            return None
        get_pct_btc_vm = self.btc * 100 / (self.valor_mercado * 1000)
        return get_pct_btc_vm

    def get_pct_termo_vm(self):
        if not self.valor_mercado or not self.btc or not self.termo:
            return None
        get_pct_termo_vm = self.termo * 100 / (self.valor_mercado * 1000)
        return get_pct_termo_vm

    def __str__(self):
            return self.ativo


class B3Taxes(models.Model):
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    b3_brokering = models.DecimalField(max_digits=9, decimal_places=8, null=True, blank=True, default=0.0)
    b3_settlement = models.DecimalField(max_digits=9, decimal_places=8, null=True, blank=True, default=0.0)
    b3_registration = models.DecimalField(max_digits=9, decimal_places=8, null=True, blank=True, default=0.0)
    @classmethod
    def get_b3_taxes(cls, date):
        try:
            b3_taxes = cls.objects.get(date_from__lte=date, date_to__isnull=True)
        except:
            b3_taxes = cls.objects.get(date_from__lte=date, date_to__gte=date)
        return (b3_taxes.b3_brokering + b3_taxes.b3_settlement + b3_taxes.b3_registration)/100


class Broker(models.Model):
    code = models.SmallIntegerField(null=True, blank=True)
    broker = models.CharField(max_length=64, null=True, blank=True)
    def get_broker_taxes(self, date, type='order'):
        try:
            bt = self.brokertaxes_set.filter(type=type).get(date_from__lte=date, date_to__isnull=True)
        except:
            bt = self.brokertaxes_set.filter(type=type).get(date_from__lte=date, date_to__gte=date)
        return bt

# Broker Brokerage Type
BBT_CHOICES = (
    ('fixed','Fixed'),
    ('order', 'Order'),
)

class BrokerTaxes(models.Model):
    broker = models.ForeignKey('Broker', on_delete=models.CASCADE)
    type =  models.CharField(max_length=12, choices=BBT_CHOICES, default='order')

    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)

    stock_brokering = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    stock_iss = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    stock_day_trade_brokerage = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    stock_day_trade_iss = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    options_trade_brokerage = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    options_trade_iss = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
