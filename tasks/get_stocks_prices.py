"""
Este script deve ir no crontab, para pegar as cotacoes do Yahoo Finance
Ele acessa as funcoes do modulo stock_price, que pega todas as acoes de todos os csvs salvos,
captura as informacoes no Yahoo e grava no DB.
"""

# coding: utf-8
from collections import defaultdict
from datetime import datetime


# To import stock_price.models from django_b3_ir_calc
import os, django
from django.conf import settings
from django_b3_ir_calc import settings as myapp_defaults
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_b3_ir_calc.settings')
django.setup()
from stock_price.models import StockPrice
from stock_price.stock_price import get_stocks, get_price, read_csvs_dir


def save_stocks(stock, price, hour):
    stock_obj, created = StockPrice.objects.get_or_create(stock=stock)
    stock_obj.price = price
    stock_obj.hour = hour
    stock_obj.last_update = datetime.now()
    stock_obj.save()


if __name__ == "__main__":
    stocks = read_csvs_dir()
    stock_price = defaultdict()
    for stock in stocks:
        try:
            (price, hour) = get_price(stock)
            if price and hour:
                save_stocks(stock, price, hour)
        except:
            pass
