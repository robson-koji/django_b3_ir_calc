import os, django
from django.conf import settings
import pandas as pd
import sys


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_b3_ir_calc.settings')
django.setup()

from reference_data.models import Cotacoes
from utils.views import send_email
from data_source.views import *



def resample(tframe, ts):
    """
    Altera o timeframe. A base eh 15min, e a partir dai gera tfs mais exparsos
    de acordo com a necessidade.
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.resample.html
    """
    return ts.resample(tframe).agg({'open':'first', 'high':'max', 'low':'min', 'close':'last', 'volume': 'sum'})


def get_stocks(tf, rsi_threshold):
    """ Recupera acoes sobrevendidas """
    # All Stocks
    stocks_lst = get_all_stocks_cleaned_SA()

    # Filter stocks by RSI
    stocks_lst = []
    get_stocks_rsi(stocks_lst, [])
    stocks_lst = [sl[0] for sl in stocks_lst if float(sl[4]) < rsi_threshold]
    return stocks_lst


def awake(sr):
    """ Verifica ativacao de compra em acoes que estao sobrevendidas """
    # print(sr.std(skipna = True))
    sr = sr['volume']

    sr = sr.iloc[::-1]

    # Remove outliers fora de 1 desvio padrão
    clean = sr.loc[((sr - sr.mean()) / sr.std()).abs() < 1]
    cl_mean = clean.mean()
    cl_std = clean.std()

    # VERIFICAR O INDICE -1 PARA VER SE EH O ULTIMO MESMO.
    # import pdb; pdb.set_trace()
    try:
        if sr.iloc[0] > cl_mean + cl_std*2:
            return(cl_mean)
            print(cl_mean)
            print(sr.iloc[0])
            print()
    except:
        pass
        # continue


def ma(span, ts):
    """ moving average
    Nao bate com o Trading View. Eles fecham o ultimo candle de forma diferente.
    """
    # ts = ts.iloc[::-1]
    # SMA
    ts = ts['close'].rolling(window=span).mean()
    # EMA
    # ts = pd.Series.ewm(ts['close'], span=span, adjust=False).mean()

    return ts


def buy_mm(ts):
    """ Sinal de compra cruzamento MM com base em tf definido para cada papel """
    (ewm_blast, ewm_last) = ma(9, ts)[-2:]
    close_blast = ts['close'][1]
    low_last = ts['low'][0]

    if low_last < ewm_last and close_blast > ewm_blast:
        print(low_last , ewm_last , close_blast , ewm_blast)
        #import pdb; pdb.set_trace()
        return True
    return False


def loop_stocks(stocks_lst, check_business):
    html = ''
    for stock in stocks_lst:
        print(stock)
        stock = stock + '.SA'
        try:
            df = pd.DataFrame(list(Cotacoes.objects.filter(stock=stock).order_by('-datetime').values()))
            ts = df.set_index('datetime')
            sr = resample(tf, ts)
        except Exception as e:
            print(e)
            continue

        # Drop row when column is NAN
        sr.dropna(subset = ["open"], inplace=True)

        # Precisa criar um app para gravar os alarmes.
        #print(buy_mm(sr))
        if check_business == 'chk_awake':
            mean = awake(sr)
            if mean:
                # import pdb; pdb.set_trace()
                html += '<b>Stock: %s </b> - Date: %s - Mean: %s - Close: %s <br>' % \
                    (stock, str(sr.index[-1]),  str(mean), str(sr['close'][-1]))
                # awake_lst.append([stock, sr.index[-1],  mean, sr['close'][-1]])
    return html


if __name__ == "__main__":
    """
    sys.argv[1] == 'chk_awake': Verifica se tem papel sobrevendido.
    """

    if sys.argv[1] == 'chk_awake':
        # Ativa compra nos 15
        tf = '15min'
        rsi_threshold = 35
        stocks_lst = get_stocks(tf, rsi_threshold)


        awake_html = loop_stocks(stocks_lst, check_business='chk_awake')        
        if awake_html:
            send_email('Awakening', awake_html)


    # Ativa compra em MM nos tempos que o mercado estah operando.
