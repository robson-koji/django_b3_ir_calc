import os, csv, django
from django.conf import settings
from django_b3_ir_calc import settings as myapp_defaults
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_b3_ir_calc.settings')
django.setup()
from stock_price.models import StockPrice


def get_stocks_from_db():
    return set(StockPrice.objects.values_list('stock', flat=True))

def get_csv_from_file():
    """ Get CVS data from CSV file. Dont have to convert always from PDF. """
    BASE_DIR = settings.BASE_DIR
    csv_dir = '/endorsement/data_11/csv/'
    try:
        out_csv =  BASE_DIR + csv_dir + 'out.csv'
        with open(out_csv, 'r') as read_obj:
            csv_reader = csv.reader(read_obj)
            list_of_rows = list(csv_reader)
        stocks = set()
        for lor in list_of_rows:
             stocks.add(lor[1])
        return stocks
    except FileNotFoundError:
        return None


db_stocks = get_stocks_from_db()
file_stocks = get_csv_from_file()

union = set.union(db_stocks, file_stocks)

with open('/var/tmp/stocks.txt', 'w') as stocks_file:
    for stock in union:
        if not 'BOVA' in stock:
            stocks_file.write("%s.SA\n" % (stock))
