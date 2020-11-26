from django.db import models

from reference_data.models import Ativos


EVT_CHOICES = (
    ('desdobramento','desdobramento'),
    ('bonificacao','bonificacao'),
    ('conversao', 'conversao')
)

class CorporateEvent(models.Model):
    # Ativo is the company, not the stock.
    # Check if it raises problems.
    asset = models.ForeignKey(Ativos, on_delete=models.CASCADE)
    event =  models.CharField(max_length=24, choices=EVT_CHOICES)
    date_ex = models.DateField(null=True, blank=True)
    date_new = models.DateField(null=True, blank=True)
    group_valid = models.SmallIntegerField(null=True, blank=True)
    operator = models.CharField(max_length=1, null=True, blank=True)
    qtt_operation = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    asset_code_old = models.CharField(max_length=12, null=True, blank=True, help_text=u"For conversao only")
    asset_code_new = models.CharField(max_length=12, null=True, blank=True, help_text=u"For conversao only")

    def __str__(self):
        return "%s - %s - %s" % (self.asset, self.event, str(self.date_ex) )
