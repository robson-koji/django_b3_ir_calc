from django.db import models

class Setorial(models.Model):
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
    """ CSV file uploaded by user (b3 CEI file) """
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
