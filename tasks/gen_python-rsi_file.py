import os, csv, django
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_b3_ir_calc.settings')
django.setup()

from data_source.views import *


db_stocks = get_stocks_from_db()
file_stocks = get_stocks_endorsement()
union = set.union(db_stocks, file_stocks)

with open('/var/tmp/stocks.txt', 'w') as stocks_file:
    for stock in union:
        if not 'BOVA' in stock:
            # print(stock)
            stocks_file.write("%s.SA\n" % (stock))
