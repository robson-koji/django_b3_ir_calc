from logging.config import valid_ident
import os, re, csv, glob
import pdb
import traceback
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
            opers = re.findall(r'Ajuste\s+D/C\n(.*?)\n\s*Resumo', s, flags=re.DOTALL)
            # pdb.set_trace()
            if len(data_pregao) != len(opers):                
                raise Exception("Erro no numero de operacoes")
            
            dict_datas = {}
            for i in range(len(data_pregao)):
                if not data_pregao[i] in dict_datas: 
                    dict_datas[data_pregao[i]] = []                    
                dict_datas[data_pregao[i]].extend(opers[i].split('\n'))
            
            return dict_datas
            

        except ValueError:
            return None

   
    stocks_name = StockPrice.objects.values_list('stock', flat=True)
    def get_stock_code(self, name:str) -> str:
        """ Retorna codigo da acao """        
        try:                        
            # Parecem ser codigos relacionados a leilao na abertura, fechamento etc...
            # Verificar se nao hah impacto no codigo do papel para efeito de calculo.
            name = name.replace(' ED ', ' ').replace(' EJ ', ' ').replace(' ERJ ', ' ')\
                .replace(' EDJ ', ' ').replace(' ATZ ', ' ').replace(' EB ', ' ')\
                .replace(' EJB ', ' ').replace(' ES ', ' ').replace(',', '')
                
            name = re.sub(' ATZ', '', name)
            name = re.sub(' D$', '', name)
            name = re.sub(' ED', '', name)
            name = re.sub(' EJ', '', name)
            name = re.sub(' ER', '', name)
            
            # Mesmo papel representado com nomes diferentes em diferentes corretoras,
            # ou ateh na mesma corretora.
            name = name.replace('HASHDEX BTC CI', 'BITCOIN HASH CI')\
                        .replace('HASHDEX ETH CI', 'ETHER HASH CI')\
                        .replace('BBSEGURIDADE ON NM', 'BBSEGURIDADE ONR NM')\
                        .replace('DIMED ON N2', 'DIMED ON')
                        
            name = re.sub('IRANI ON$', 'IRANI ON NM', name)

                        
            stock_code = self.stocks_name.get(name=name)
            return stock_code
        except StockPrice.DoesNotExist:
            # Use name as stock_code
            raise StockPrice.DoesNotExist('Using name as stock_code: {}'.format(name))                        
        except StockPrice.MultipleObjectsReturned:
            raise Exception('StockPrice.MultipleObjectsReturned: {}'.format(name))
        

    def validate_fields(self, dict_oper):                   
        for k, v in dict_oper.items():
            if k != 'obs' and k != 'prazo' and not v:
                raise Exception("dict_oper'['d_c'] - Key is empty:  {} - {}".format(k, dict_oper))


    def get_fields(self, corretora:str, data:str, values:str) -> dict:  
        """
        Nao consegue pegar RICO e MIRAE com os mesmos filtros (posicional ou regex).
        Rico nao funciona posicional, nem soh com as proprias notas de corretagem.
        
        Rico e Miran, nao funciona o mesmo regex. (talvez de para funcionar, mas precisaria elaborar melhor)
        """

        if corretora == 'Rico':
            
            
            # Daytrade - Utilizar posteriormente
            values = values.replace('  D#2   ', '     ')
            values = values.replace('#', ' ')
            values = values.replace('  D   ', '     ')
            
            try:
                regex = r'(?P<negociacao>.+?)\s+?(?P<c_v>\w+?)\s+(?P<tipo_mercado>\w+?)\s+(?P<esp_titulo>.+?)\s{30,}(?P<qt>\d+\.*\d+|\d+)\s+(?P<preco>.+?)\s+(?P<valor_oper>.+?)\s(?P<d_c>\w+)'                
                match = re.search(regex, values)
                esp_titulo = re.sub(r'\s+', ' ', match.group('esp_titulo')).replace('#', '')            
                stock_code = self.get_stock_code(esp_titulo)                
            except StockPrice.DoesNotExist:
                raise IndexError('Erro no regex: {}'.format(values))        
            except Exception:
                pdb.set_trace()                       

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
            return dict_oper

        elif corretora == 'Mirae':
            name = re.sub(r'\s+', ' ', values[81:135].strip())

            try:
                stock_code = self.get_stock_code(name)
            except StockPrice.DoesNotExist:
                # print (values)
                # pdb.set_trace()
                stock_code = name.replace(' ', '_').replace(',', '_')
                
            """
            Exemplos com espacamentos reais
            1-BOVESPA                C OPCAO DE VENDA                           04/20 BOVAP65                             CI 65,00 BOVAE                                  200                        2,81                       562,00 D'
            1-BOVESPA                V  VISTA                                           ETHER HASH                        CI                                              21                       50,84                    1.067,64     C'
            1-BOVESPA                V  VISTA                                           PROFARMA                           ON     NM               #                      100                        6,48                       648,00    C
            1-BOVESPA                C VISTA                                            CSNMINERACAO                      ON    N2                                    1.000                        7,16                    7.160,00 D
            1-BOVESPA                  V     VISTA                                      EVEN        ON NM                                                 1.000                  5,44                              5.440,00        C
            1-BOVESPA                   C VISTA                                           VALE        ON NM                                                 100                  83,99                               8.399,00        D
            1-BOVESPA                   C      VISTA                                      EZTEC          ON NM                                              100                  20,66                               2.066,00        D
            """
        
            dict_oper = {'data':data.strip(),
                        'negociaco':values[0:32].strip(), 
                        'c_v':values[32:34].strip(), 
                        'tipo_mercado':values[34:75].strip(), 
                        'prazo':values[75:81].strip(), 
                        'codigo':stock_code, 
                        'obs':values[135:160].strip(), 
                        'qt':values[160:175].strip(), 
                        'preco':values[175:200].strip(), 
                        'valor_oper':values[-3:-25:-1].strip()[::-1], 
                        'd_c':values[-1:-3:-1].strip()}
            try:
                self.validate_fields(dict_oper)
            except:
                raise           
        
            return dict_oper

    def process_files(self, corretora, file):
        # file = '/home/robson/irpf/NotasCorretagem/Rico/NotasCorretagem/202105.pdf'
        pdf_content = self.read_pdf(file)
        dict_datas = self.find_between(pdf_content)
        
        opers = []
        for data, values in dict_datas.items():
            for v in values:
                oper = self.get_fields (corretora, data, v)
                opers.append(oper)
        opers.reverse()                
        return opers
        


if __name__ == '__main__':
    TIPO_MERCADO = {'VISTA':'VIS', 'OPCAO DE VENDA': 'OPC'}
    
    corretora = 'Rico'    
    corretoras={
                'Rico':{'codigo':'386',
                        'files':'/home/robson/irpf/NotasCorretagem/Rico/NotasCorretagem/*.pdf'},
                'Mirae':{'codigo':'262',
                         'files':'/home/robson/irpf/NotasCorretagem/Mirae/NotasCorretagem/*.pdf'}}

    linha_1 = '{}, "", "",  "",  "",  "",  "",  "",  ""\n'.format(corretoras[corretora]['codigo'])
    FILES = glob.glob(os.path.join(corretoras[corretora]['files']))
    
    b2c = Broker_2_Cei()
    FILES.sort(reverse=True)    
    csv_complete = linha_1
    for file in FILES:
        
        opers = b2c.process_files(corretora, file)           
        try:
            for oper in opers:
                # print(oper)
                
                oper = '{},"",{},{},{},"",{},"{}","{}"'.format(oper['data'], oper['c_v'], TIPO_MERCADO[oper['tipo_mercado']], oper['codigo'], oper['qt'], oper['preco'], oper['valor_oper'])
                if oper:
                    # print('----', oper)
                    csv_complete += oper + '\n'      
        except KeyError:
            print(traceback.format_exc())
            print(oper)
            print('KeyError')
            pdb.set_trace()
            raise
        except TypeError:
            print(traceback.format_exc())
            print(oper)
            print('KeyError')
            pdb.set_trace()
       
    csv_complete = csv_complete[:-1]
    

    print(csv_complete)
    