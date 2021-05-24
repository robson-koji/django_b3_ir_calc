
# To import stock_price.models from django_b3_ir_calc

import pymysql
import os, django
import numpy as np
import pandas as pd
import yfinance as yf

from django.conf import settings
from sqlalchemy import create_engine

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_b3_ir_calc.settings')
django.setup()

from reference_data.models import Cotacoes
from data_source.views import get_all_stocks_cleaned_SA

stocks_lst = get_all_stocks_cleaned_SA()
# stocks_lst = ['PETR4.SA', 'BRFS3.SA']

stocks_str = ' '.join(stocks_lst)
# stocks_str = 'PETR4.SA BRFS3.SA'


def get_data():
    data = yf.download(  # or pdr.get_data_yahoo(...
            # tickers list or string as well
            tickers = stocks_str,

            # use "period" instead of start/end
            # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            # (optional, default is '1mo')
            period = "1d",

            # fetch data by interval (including intraday if period < 60 days)
            # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            # (optional, default is '1d')
            interval = "5m",

            # group by ticker (to access via data['SPY'])
            # (optional, default is 'column')
            group_by = 'ticker',

            # adjust all OHLC automatically
            # (optional, default is False)
            auto_adjust = True,

            # download pre/post regular market hours data
            # (optional, default is False)
            prepost = True,

            # use threads for mass downloading? (True/False/Integer)
            # (optional, default is True)
            threads = True,

            # proxy URL scheme use use when downloading?
            # (optional, default is None)
            proxy = None
        )
    return data


if __name__ == "__main__":
    data = get_data()
    for stock in stocks_lst:
        if not stock in data.keys():
            continue
        # import pdb; pdb.set_trace()
        for i, row in data[stock].iterrows():
            try:
                if np.isnan(row['Open']):
                    row['Open'] = row['High'] = row['Low'] = row['Close'] = prev_row['Close']
                Cotacoes.objects.get_or_create(
                        stock = stock, datetime = i,
                        open = row['Open'], high = row['High'],
                        low = row['Low'], close = row['Close'],
                        volume = row['Volume']
                )
            except:
                continue
            prev_row = row

        	# print(f"Index: {i}")
        	# print(f"{row['Open']}")
