from django.db import models
from datetime import date, datetime

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
    indice = models.ManyToManyField('Indice')

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

# Broker Brokerage Type
B3MKT_CHOICES = (
    ('regular','Regular Trade'),
    ('daytrade', 'Day Trade'),
)

class B3Taxes(models.Model):
    """
    Nesta pg, o arquivo BVBG.072.01 deveria ter os custos da B3, porem na data de 14/02/21, nao tem a liquidacao para acoes a vista.
    http://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/boletins-diarios/pesquisa-por-pregao/pesquisa-por-pregao/
    """
    type =  models.CharField(max_length=12, choices=B3MKT_CHOICES, default='regular')

    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    b3_brokering = models.DecimalField(max_digits=9, decimal_places=8, null=True, blank=True, default=0.0)
    b3_settlement = models.DecimalField(max_digits=9, decimal_places=8, null=True, blank=True, default=0.0)
    b3_registration = models.DecimalField(max_digits=9, decimal_places=8, null=True, blank=True, default=0.0)
    @classmethod
    def get_b3_taxes(cls, type, date):
        try:
            b3_taxes = cls.objects.get(type=type, date_from__lte=date, date_to__isnull=True)
        except:
            b3_taxes = cls.objects.get(type=type, date_from__lte=date, date_to__gte=date)
        return (b3_taxes.b3_brokering + b3_taxes.b3_settlement + b3_taxes.b3_registration)/100

    def __str__(self):
        return "%s até: %s" % (self.type, (self.date_to))

class Broker(models.Model):
    code = models.SmallIntegerField(null=True, blank=True)
    broker = models.CharField(max_length=64, null=True, blank=True)
    def get_broker_taxes(self, date, type='order'):
        # import pdb; pdb.set_trace()
        try:
            bt = self.brokertaxes_set.filter(type=type).get(date_from__lte=date, date_to__isnull=True)
        except:
            bt = self.brokertaxes_set.filter(type=type).get(date_from__lte=date, date_to__gte=date)
        return bt

    def __str__(self):
        return "%i: %s" % (self.code, self.broker)
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

    def __str__(self):
        return "%s: %s - De: %s - Ate: %s" % (self.broker, self.type, self.date_from, self.date_to)

IDX_CHOICES = (
    ('ICON', 'Consumo'),
    ('IEEX', 'Energia'),
    ('IFNC','Financeiro'),
    ('IMOB', 'Imobiliário'),
    ('IMAT', 'Materiais Básicos'),
    ('SMLL', 'Small'),
    ('UTIL', 'Utilities'),
)

class Indice(models.Model):
    indice = models.CharField(max_length=12, choices=IDX_CHOICES, default='order')
    def __str__(self):
            return self.indice


class Cotacoes(models.Model):
    stock = models.CharField(max_length=12, null=True, blank=True)
    datetime = models.DateTimeField()
    open = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    high = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    low = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    close = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('stock', 'datetime') 
