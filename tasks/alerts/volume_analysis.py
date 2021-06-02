import sys
import os, django
import pandas as pd
from datetime import date

from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_b3_ir_calc.settings')
django.setup()

from reference_data.models import Cotacoes
from utils.views import send_email
from data_source.views import *
from alerts.models import *


def resample(tframe, ts):
    """
    Altera o timeframe. A base eh 15min, e a partir dai gera tfs mais exparsos
    de acordo com a necessidade.
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.resample.html
    """
    ts = ts.tz_convert('America/Sao_Paulo')
    return ts.resample(tframe, origin='start').agg({'open':'first', 'high':'max', 'low':'min', 'close':'last', 'volume': 'sum'})

def get_stocks(rsi_threshold):
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





def loop_stocks_awake(tframe, stocks_lst, check_business):
    html = ''
    for stock in stocks_lst:
        # print(stock)
        stock = stock + '.SA'
        try:
            df = pd.DataFrame(list(Cotacoes.objects.filter(stock=stock).order_by('-datetime').values()))
            ts = df.set_index('datetime')
            sr = resample(tframe, ts)
        except Exception as e:
            print(e)
            continue

        # Drop row when column is NAN
        sr.dropna(subset = ["open"], inplace=True)

        if check_business == 'chk_awake':
            mean = awake(sr)

            if mean:
                p, created = SendAlert.objects.get_or_create(date=date.today(),
                                                            stock=stock,
                                                            alert='awake',
                                                            desc='Stock: %s - Date: %s - Mean: %s - Close: %s' % \
                                                                (stock, str(sr.index[-1]),  str(mean), str(sr['close'][-1]))
                                                            )
                # Envia somente uma vez por dia.
                if created:
                    html += '<b>Stock: %s </b> - Date: %s - Mean: %s - Close: %s <br>' % \
                        (stock, str(sr.index[-1]),  str(mean), str(sr['close'][-1]))
    return html




# def get_mmalert():
def buy_mm(ts):
    """ Sinal de compra cruzamento MM com base em tf definido para cada papel """
    (ewm_blast, ewm_last) = ma(9, ts)[-2:]
    close_blast = ts['low'][-2]
    low_last = ts['low'][-1]

    print("ewm_blast: %s" % (str(ewm_blast)))
    print("ewm_last: %s" % (str(ewm_last)))
    print("low_last: %s" % (str(low_last)))
    print("close_blast: %s" % (str(close_blast)))

    #import pdb; pdb.set_trace()
    if low_last < ewm_last and close_blast > ewm_blast:
        return True
    return False


def loop_stocks_mm_alert(stocks_lst):
    html = ''
    for stk in stocks_lst:

        if stk.stock != 'WEGE3':
            continue

        stock = stk.stock + '.SA'
#        print(stock)
        try:
            df = pd.DataFrame(list(Cotacoes.objects.filter(stock=stock).order_by('-datetime').values()))
            ts = df.set_index('datetime')
            sr = resample(stk.timeframe, ts)
        except Exception as e:
            print(e)
            continue

        # Drop row when column is NAN
        sr.dropna(subset = ["open"], inplace=True)

        mean = stk.smm if stk.smm else stk.emm
        print( stock )
        print( mean )
        if buy_mm(sr):
            p, created = SendAlert.objects.get_or_create(date=date.today(),
                                                        stock=stock,
                                                        alert='mm_alert',
                                                        desc='Stock: %s - Date: %s - Mean: %s - Low: %s - Timeframe: %s' % \
                                                            (stock, str(sr.index[-1]), str(mean), str(sr['low'][-1]), str(stk.timeframe[-1]))
                                                        )
            # Envia somente uma vez por dia.
            if created:
                html += '<b>Stock: %s </b> - Date: %s - Mean: %s - Low: %s - Timeframe: %s <br>' % \
                    (stock, str(sr.index[-1]), str(mean), str(sr['low'][-1]), str(stk.timeframe[-1]))
    return html



if __name__ == "__main__":
    """
    sys.argv[1] == 'chk_awake': Verifica se tem papel sobrevendido.
    sys.argv[1] == 'mm_alert': Verifica se tem papel sobrevendido.
    """

    if sys.argv[1] == 'chk_awake':
        # Ativa compra nos 15
        tframe = '15min'
        rsi_threshold = 35
        stocks_lst = get_stocks(rsi_threshold)
        awake_html = loop_stocks_awake(tframe, stocks_lst, check_business='chk_awake')
        if awake_html:
            send_email('Awakening', awake_html)

    if sys.argv[1] == 'mm_alert':
        stocks_lst = MmAlert.objects.filter(active=True)
        #stocks_lst = mm_alerts.values_list('stock', flat=True)
        mm_alert_html = loop_stocks_mm_alert(stocks_lst)
        if mm_alert_html:
            send_email('MM Alert', mm_alert_html)



    # Ativa compra em MM nos tempos que o mercado estah operando.
