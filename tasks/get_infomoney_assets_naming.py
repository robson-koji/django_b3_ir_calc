"""
Este script recupera as acoes em uso, no db, e verifica se encontra no infomoney.
Se encontrar, captura o nome e grava no banco.
Se nao conseguir achar, precisa preencher na mao, por enquanto.

!!! Pegando do investnews. Por enquanto OK.
"""

import os, pdb, django
import bs4, json, requests
# from urllib2 import urlopen
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime, date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_b3_ir_calc.settings')
django.setup()
# from data_source.views import get_all_stocks_cleaned_SA
from stock_price.models import StockPrice


"""    
def teste_acao_list():
    with open('test_files/infomoney_b3.html', 'r') as infomoney_file:
        soup = bs4.BeautifulSoup(infomoney_file,'html.parser')
        return soup


def teste_acao_detail():
    with open('test_files/acao_detail.htm', 'r') as infomoney_file:
        soup = bs4.BeautifulSoup(infomoney_file,'html.parser')
        return soup




def get_b3_list(dev=False):    
    !!! - Lista completamente desatualizada

    if dev:
        soup = teste_acao_list()    
    else:
        # url = 'https://www.infomoney.com.br/cotacoes/empresas-b3/' % (stock)
        url = 'https://www.infomoney.com.br/cotacoes/empresas-b3/'
        try:
            page = requests.get(url)
        except:
            print('Error opening the URL')
        soup = bs4.BeautifulSoup(page.content,'html.parser')


    # bs4 get all divs with class 'list-companies'
    divs = soup.findAll('div',{'class': 'list-companies'})

    # Get all descendants of divs where class equals to strong
    setor = []
    children = []
    setores = defaultdict(list)
    for div in divs:
        setor = div.get('id')
        # print(div)
        children = div.find_all('td', {'class': 'strong'})
        stocks = []
        for e in children:
            # check if txt not empty, or last char of txt is a letter
            txt = e.a.text.strip()
            if not txt or txt[-1].isalpha() : 
                continue
            # print (e.a)
            stocks.append(e.a)
        setores[setor] = stocks
    # print(setores.keys())
    return setores    
"""

def get_b3_detail(stock=None, dev=False):
    """
    !!! Nao acha todos. Preenchendo na mao os que nao acha.
    """
    if dev:
        pass
        # soup = teste_acao_detail()    
    else:
        try:
            url = 'https://investnews.com.br/?s=%s' % (stock)

            # url = 'https://www.infomoney.com.br/%s' % (stock) --> Infomoney
            page = requests.get(url, allow_redirects=True, timeout=10)
        except Exception as e:
            print(e)
            print('Error opening the URL')
            
        soup = bs4.BeautifulSoup(page.content,'html.parser')
    try:
        
        return (soup.find('div',{'class': 'acao-desc'}).text) #--> InvestNews
        #return (soup.find('p',{'class': 'stock-name'}).text) --> Infomoney
    except AttributeError:
        return None


def save_stocks(stock, name, setor):
    try:
        stock_obj = StockPrice.objects.get(stock=stock)
        stock_obj.name = name
        stock_obj.sector = setor
        stock_obj.save()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    empty_names =  set(StockPrice.objects.filter(name__isnull=True).values_list('stock', flat=True))
    # setores = get_b3_list(dev=True)

    # pdb.set_trace()

    for stock in empty_names:            
        print (stock)
        stock_name = get_b3_detail(stock, dev=False)
        save_stocks(stock, stock_name, None)
        
        # pdb.set_trace()



