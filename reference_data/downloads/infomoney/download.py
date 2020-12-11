import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_b3_ir_calc.settings")
django.setup()

from bs4 import BeautifulSoup
import requests, re, sys, string

from reference_data.models import *


indices = {
    'ICON': 'https://www.infomoney.com.br/cotacoes/icon/' ,
    # 'IEEX': ,
    'IFNC': 'https://www.infomoney.com.br/cotacoes/ifnc/' ,
    'IMOB': 'https://www.infomoney.com.br/cotacoes/imob/' ,
    'IMAT': 'https://www.infomoney.com.br/cotacoes/imat/' ,
    'SMLL': 'https://www.infomoney.com.br/cotacoes/smll/' ,
    'UTIL': 'https://www.infomoney.com.br/cotacoes/util/',
    'INDX': 'https://www.infomoney.com.br/cotacoes/indx/',    
    }


req_session = requests.Session()

def download(indice, url):
    r = req_session.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    table_high = soup.find("table",{"id":"high"})
    trs = table_high.find_all('tr')
    table_low = soup.find("table",{"id":"low"})
    trs +=  table_low.find_all('tr')

    indice = Indice.objects.get(indice=indice)
    for tr in trs:
        try:
            stock = tr.findAll('a')[0].string
            ativo = stock.rstrip(string.digits)
            ativo = Ativos.objects.get(ativo=ativo)
            ativo.indice.add(indice)
        except:
            continue


# Delete all M2M relations.
Ativos.indice.through.objects.all().delete()
for indice in indices:
    download(indice, indices[indice])
