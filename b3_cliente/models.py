from django.db import models
from django.contrib.auth.models import User

from reference_data.models import Broker

class B3Cliente(models.Model):
    """ Cliente da corretora. Dados do B3 CEI. """
    user = models.ForeignKey(User)
    participante = models.ForeignKey('Broker', on_delete=models.CASCADE)
    cliente_codigo = models.IntegerField('Códido do cliente')
    cliente_nome = models.CharField('Nome do cliente', max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class B3Cei(models.Model):
    """ Arquivo CEI do B3Cliente. """
    cliente = models.ForeignKey('B3Cliente', on_delete=models.CASCADE)
    date = models.DateField('Data', null=True, blank=True)
    oper = models.CharField('Operação', max_length=2)
    type = models.CharField('Operação', max_length=32)
    stock = models.CharField('Operação', max_length=32)
    qt = models.IntegerField('Códido do cliente')
    unit_price = models.DecimalField(max_digits=7, decimal_places=2)
    value = models.DecimalField(max_digits=9, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
