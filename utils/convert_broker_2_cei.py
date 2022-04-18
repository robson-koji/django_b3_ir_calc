import os, re, csv, glob
import pdb
import pdftotext
from django.conf import settings

import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_b3_ir_calc.settings')
django.setup()
from stock_price.models import StockPrice



class Broker_2_Cei():
    """
    Receive list of pdfs and return CSV CEI formated
    """

    def read_pdf(self, pdf_file):
        """
        Le arquivo PDF, e converte pg por pg para texto.
        Retorna lista de lista para criar arquivo CSV.
        """
        with open(pdf_file, "rb") as f:
            pdf = pdftotext.PDF(f)

        pdf_txt = ''
        for pg in pdf:
            pdf_txt += pg
            # print (pg)
        # print(pdf_txt)
        return pdf_txt


    def find_between(self, s:str, first:str='D/C\n', last:str='Resumo dos Negócios') -> dict:
        try:
            # Recupera data das operacoes
            data_pregao = re.findall(r'Data pregão\n\s+\d+\s+\d\s+(.*?)\n', s, flags=re.DOTALL)

            # Recupera operacoes
            opers = re.findall(r'D/C\n(.*?)\nResumo', s, flags=re.DOTALL)

            dict_datas = dict(zip(data_pregao, opers))
           
            for k, v in dict_datas.items():
                dict_datas[k] = v.split('\n')

            return dict_datas    
        except ValueError:
            return None

   
    stocks_name = StockPrice.objects.values_list('stock', flat=True)
    def get_stock_code(self, name:str) -> str:
        """ Retorna codigo da acao """        
        try:            
            name = name.replace(' ED ', ' ').replace(' EJ ', ' ')
            name = name.replace('B3 ON NM D', 'B3 ON NM')
            stock_code = self.stocks_name.get(name=name)
            return stock_code
        except StockPrice.DoesNotExist:
            print(name)            
            # pdb.set_trace()
            return None


    def get_fields(self, data:str, values:str) -> list:            
        regex = r'(?P<negociacao>.+?)\s+?(?P<c_v>\w+?)\s+(?P<tipo_mercado>\w+?)\s+(?P<esp_titulo>.+?)(?P<qt>\d+\.*\d+)\s+(?P<preco>.+?)\s+(?P<valor_oper>.+?)\s(?P<d_c>\w+)'
        match = re.search(regex, values)
        if match:
            esp_titulo = re.sub(r'\s+', ' ', match.group('esp_titulo')).replace('#', '')            
            stock_code = self.get_stock_code(esp_titulo.strip())
            
            dict_oper = {'data':data.strip(),
                         'esp_titulo':esp_titulo.strip(), 
                        'codigo':stock_code,
                        'negociaco':match.group('negociacao').strip(), 
                        'c_v':match.group('c_v').strip(), 
                        'tipo_mercado':match.group('tipo_mercado').strip(), 
                        'qt':match.group('qt').strip(), 
                        'preco':match.group('preco').strip(), 
                        'valor_oper':match.group('valor_oper').strip(), 
                        'd_c':match.group('d_c').strip()}
        else:
            print('No match')        
        return dict_oper




if __name__ == '__main__':

    b2c = Broker_2_Cei()
    # 202012
    # 202107
    asdf = b2c.read_pdf('/home/robson/irpf/NotasCorretagem/Rico/202012.pdf')

    dict_datas = b2c.find_between(asdf)


    # import pdb; pdb.set_trace()
    
    opers = []

    for data, values in dict_datas.items():
        # use filter function to remove empty strings on x
        # x = list(filter(None, x))
        
        # pdb.set_trace()
        for v in values:
            oper = b2c.get_fields (data, v)
            opers.append(oper)
    list(map(print, opers))



"""
IRBR3
BBSE3
ITSA4
"""


"""
Por aqui dah!!! Fazer o reverso
https://www.infomoney.com.br/cotacoes/empresas-b3/
./b3_ir_calc/b3_ir_calc/get_b3_list.py:    url = 'https://www.infomoney.com.br/cotacoes/empresas-b3/' % (stock)

!!! - tem a especificacao do titulo - buscar pelo codigo.
    https://investnews.com.br/cotacao/mglu3-magazine-luiza/


    !!! Aqui tem tudo de acoes.
    https://br.advfn.com/forum/ibopv/68827/1 - é de 2006


    !!! ETF deve dar um puta trabvalho. 
    Talve melhor fazer na mao, por enquanto
    Nao dah por aqui e nao tem em nenhum lugar. p. ex ETHE11:
    https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/etf/renda-variavel/etfs-listados/

"""