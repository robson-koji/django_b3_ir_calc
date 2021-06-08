# coding: utf-8

import glob, csv
import bs4, json, requests

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from collections import defaultdict
from datetime import datetime, date


from data_source.views import get_stocks_from_user_file


def read_csvs_dir():
    """ Get stocks from all csv files """
    csvs_path = '/var/www/media/b3_ir_calc/documents/'

    stocks = set()
    for filename in glob.iglob(csvs_path + '**/*.csv', recursive=True):
        print(filename)
        get_stocks_from_user_file(filename, stocks)

    return (stocks)


def get_headers():
    return {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
            "cache-control": "max-age=0",
            "dnt": "1",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"}



def get_price(stock):
    """ Get stock prices on Yahoo Finance """

    # stock = 'KLBN11'
    url = 'https://finance.yahoo.com/quote/%s.sa' % (stock)
    # import pdb; pdb.set_trace()
    try:
        # print(url)
        #page = urlopen(url)
        page = requests.get(url, headers=get_headers())
        soup = bs4.BeautifulSoup(page.content,'html.parser')
        price = soup.find('div',{'class': 'My(6px) Pos(r) smartphone_Mt(6px)'}).find('span').text
        hour = soup.find('div',{'class': 'My(6px) Pos(r) smartphone_Mt(6px)'}).findAll('span')[-1].text
        # import pdb; pdb.set_trace()
        return (price, hour)
    except AttributeError:
        print(url)
        print('Error opening the URL')
        return (None, None)



# def save_json(stock_price):
#     """ Save stock price to a JSON file """
#
#     # Alterar aqui para fazer um merge de arquivos com base na chave (acao).
#     # Se nao pegar preco novo, usar o antigo. data passa a ser atributo do objeto.
#     # Problema eh tipo bmgb11, que deixa de existir.
#     now = datetime.now().date()
#     dict_json = {str(now): stock_price}
#     with open('/var/tmp/stock_price.json', 'w') as fp:
#         json.dump(dict_json, fp)
#


def save_stocks(stock, price, hour):
    stock_obj, created = StockPrice.objects.get_or_create(stock=stock)
    stock_obj.price = price
    stock_obj.hour = hour
    stock_obj.last_update = datetime.now()
    stock_obj.save()



if __name__ == "__main__":
    import argparse

    def get_args():
        """
        To get stock prices from your CSV file, call this script wiht arguments.
        python stock_price.py --path --file
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('--mkt_type', default='VIS')
        parser.add_argument('--path', default='test_sample')
        parser.add_argument('--file', default='sample.csv')
        args = parser.parse_args()
        return args

    args = get_args()
    #stocks = get_stocks(mkt_type=args.mkt_type, path=args.path, file=args.file)
    stocks = read_csvs_dir()
    stock_price = defaultdict()
    for stock in stocks:
        try:
            (price, hour) = get_price(stock)
            stock_price[stock] = {'price': price, 'hour': hour}
        except:
            pass

        # import pdb; pdb.set_trace()
        # save_stocks(stock, price, hour)


    # save_json(stock_price)
