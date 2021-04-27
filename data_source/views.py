import csv

from django.conf import settings



def get_stocks_from_db():
    # Evita import circular
    from stock_price.models import StockPrice
    return set(StockPrice.objects.values_list('stock', flat=True))


def get_stocks_endorsement():
    """ Get stocs from CSV endorsement file """
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


def get_stocks_from_user_file(filename, stocks):
    """ Read users CSV file """

    def hasNumbers(inputString):
        return any(char.isdigit() for char in inputString)

    with open(filename) as file_handler:
        csv_reader = csv.reader(file_handler, quotechar='"', delimiter=',')
        for line in csv_reader:
            # print(line)
            if '.' in line[4] or 'null' in line[4]:
                continue

            if not hasNumbers(line[4]):
                continue

            stocks.add(line[4].split()[0])


def get_stocks_rsi(todas_acoes, acoes_com_status):
    with open("/var/tmp/stocks_rsi.txt") as f:
        for row in f:
            try:
                fields  = row.split()
                if not '.SA' in fields[0]:
                    continue
                fields[0] = fields[0].replace('.SA', '')

                if len(fields) < 7:
                    last = fields[5]
                    fields[5] = ' '
                    fields.append(last)
                else:
                    acoes_com_status.append(fields[0])

                todas_acoes.append(fields)
            except:
                pass
