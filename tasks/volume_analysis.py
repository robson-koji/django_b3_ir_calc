import os, django
from django.conf import settings
import pandas as pd


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_b3_ir_calc.settings')
django.setup()

from reference_data.models import Cotacoes
from data_source.views import get_all_stocks_cleaned_SA

stocks_lst = get_all_stocks_cleaned_SA()


for stock in stocks_lst:
    cotacoes = Cotacoes.objects.filter(stock=stock).order_by('-datetime').values_list('volume', flat=True)[:200]

    sr = pd.Series(cotacoes)
    # print(sr.std(skipna = True))

    # Remove outliers fora de 1 desvio padrão
    clean = sr.loc[((sr - sr.mean()) / sr.std()).abs() < 1]
    cl_mean = clean.mean()
    cl_std = clean.std()


    if sr.iloc[10] > cl_mean + cl_std*2:
        print(stock)
        print(cl_mean)
        print(sr.iloc[0])
        print()
    # import pdb; pdb.set_trace()
