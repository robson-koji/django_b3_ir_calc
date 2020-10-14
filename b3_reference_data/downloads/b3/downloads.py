import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_b3_ir_calc.settings")
django.setup()

from pandas.api.types import is_numeric_dtype
from collections import defaultdict
from datetime import datetime, date, timedelta
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from zipfile import ZipFile
from decimal import Decimal

import requests, re, sys, string
import pandas as pd

from b3_reference_data.models import *

class downloadMain():
    def __init__(self):
        self.req_session = requests.Session()
        # Find download_url by id or text. Depends on page layout.
        self.link_text_to_find = ''
        self.link_id = ''
        self.files_dir_path = 'b3_reference_data/downloads/b3/files/'
        self.b3_domain = 'http://b3.com.br/'

    def get_download_url(self):
        """ Algumas paginas colocam a URL de download em a href, outras em form/post"""
        r = self.req_session.get(self.pg_url)
        soup = BeautifulSoup(r.content, 'html.parser')

        if self.link_id:
            self.download_url = soup.find_all('a', attrs = {'id': self.link_id})[0].get('href')
        elif self.link_id_form:
            self.download_url = soup.find_all('form', attrs = {'id': self.link_id_form})[0].get('action')
        elif self.link_text_to_find:
            links = soup.find_all("a")
            for link in links:
                if self.link_text_to_find in link.text:
                    self.download_url = self.b3_domain + link.get('href').replace('../', '')

    def get_zipped_file(self, zipped_archive):
        with ZipFile(zipped_archive, 'r') as zipObj:
           listOfiles = zipObj.namelist()
           return listOfiles

    def unzip_file(self, zipped_file):
        with ZipFile(zipped_file, 'r') as zipObj:
            zipObj.extractall(path= self.files_dir_path)

    def get_filename_from_headers(self):
        d = self.response.headers['content-disposition']
        self.filename = re.findall("filename=(.+)", d)[0].replace('"', '')

    def get_filename_from_url(self):
        p = urlparse(self.download_url);
        self.filename = p.path.rsplit("/", 1)[-1]


class classifSetorial(downloadMain):
    def __init__(self):
        super(classifSetorial, self).__init__()
        self.pg_url = 'http://bvmf.bmfbovespa.com.br/cias-listadas/empresas-listadas/BuscaEmpresaListada.aspx?opcao=1&indiceAba=1&Idioma=pt-br'
        self.link_id = 'ctl00_contentPlaceHolderConteudo_BuscaSetorEmpresa1_lnkDownload'

    def download(self):
        # Download zipped archive
        self.get_download_url()
        self.response = self.req_session.get(self.download_url, allow_redirects=True)
        self.get_filename_from_headers()
        zipped_archive = self.files_dir_path + "%s" % (self.filename)
        open(zipped_archive, 'wb').write(self.response.content)

        # Check zipped archive lenght
        listOfiles = self.get_zipped_file(zipped_archive)
        if len(listOfiles) != 1:
            # Wait for one zipped file only
            raise IndexError('list index out of range')

        self.file + "/%s" % (listOfiles[0])

        # Unzip file
        self.unzip_file(zipped_archive)

    def read_csv(self):
        #self.file = 'b3_reference_data/downloads/b3/files/Setorial B3 05-10-2020 (português).xlsx'
        df = pd.read_excel(self.file, sheet_name=0)
        setores = defaultdict(lambda: defaultdict(dict))
        setor = subsetor = segmento = ''
        for index, row in df.iterrows():
            if pd.isna(row[3]) and pd.notna(row[2]):
                if pd.notna(row[0]):
                    setor = row[0]
                if pd.notna(row[1]):
                    subsetor = row[1]
                if pd.isna(row[3]):
                    segmento = row[2]
                setores[setor][subsetor][segmento] = []
            elif setor and subsetor and segmento and pd.notna(row[3]):
                try:
                    setores[setor][subsetor][segmento].append((row[2], row[3]))
                except Exception as e:
                    print(e)
                    import pdb; pdb.set_trace()
            elif pd.isna(row[2]):
                setor = subsetor = segmento = ''
        self.setores = setores

    def store_data(self):
        setores = self.setores
        for setor in setores:
            try:
                set_obj, created = Setorial.objects.get_or_create(
                    setor = setor,
                    pai_id__isnull = True
                )
                for subsetor in setores[setor]:
                    subs_object, created = Setorial.objects.get_or_create(
                        setor = subsetor,
                        pai = set_obj
                    )
                    for segmento in setores[setor][subsetor]:
                        seg_obj, created = Setorial.objects.get_or_create(
                            setor = segmento,
                            pai = subs_object
                        )
                        for ativo in setores[setor][subsetor][segmento]:
                            ati_obj, created = Ativos.objects.get_or_create(
                                chave_1 = ativo[0].replace(' ',''),
                                ativo = ativo[1].replace(' ', ''),
                                setorial = seg_obj
                            )
            except Exception as e:
                print(e)





class valorMercado(downloadMain):
    def __init__(self):
        super(valorMercado, self).__init__()
        self.pg_url = 'http://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/consultas/mercado-a-vista/valor-de-mercado-das-empresas-listadas/bolsa-de-valores/'
        self.link_text_to_find = 'Histórico diário'

    def download(self):
        self.get_download_url()
        self.response = self.req_session.get(self.download_url, allow_redirects=True)
        self.get_filename_from_url()
        self.file = self.files_dir_path + "%s" % (self.filename)
        open(self.file, 'wb').write(self.response.content)

    def read_csv_store_valor_mercado(self):
        #self.file = 'b3_reference_data/downloads/b3/files/VMDiadet%20-%202020-10-08.xlsx'
        df = pd.read_excel(self.file, sheet_name=0, dtype={'Unnamed: 4': str})

        for index, row in df.iterrows():
            if pd.notna(row[3]):
                chave_1 = row[3].replace(' ','')
                try:
                    ativo = Ativos.objects.get(chave_1=chave_1)
                except Exception as e:
                    continue
                ativo.valor_mercado = row[4]
                ativo.save()

class PdTableMixin():
    def from_tables_get_ativos(self):
        df = pd.read_html(str(self.table_data), decimal=',', thousands='.')
        df = df[0]

        self.ativos = defaultdict(Decimal)
        for index, row in df.iterrows():
            row[0] = row[0][:-1]
            ativo = row[0].rstrip(string.digits)
            self.ativos[ativo] += Decimal(row[self.column_data])



class Aluguel(downloadMain, PdTableMixin):
    # column_data = 4
    def __init__(self):
        super(Aluguel, self).__init__()
        self.column_data = 4
        self.today = (date.today() - timedelta(days=1)).strftime("%d/%m/%Y")
        #self.pg_url = 'http://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/consultas/mercado-a-vista/termo/posicoes-em-aberto/'
        self.pg_url = 'http://www.b3.com.br/pt_br/produtos-e-servicos/emprestimo-de-ativos/renda-variavel/posicoes-em-aberto/renda-variavel-8AE490C9701B5B35017039842ACE1F91.htm?data=%s&f=0' % (self.today)

    def get_pg_data(self):
        # import pdb; pdb.set_trace()
        r = self.req_session.get(self.pg_url)
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find_all('table', attrs = {'class': 'responsive'})
        self.table_data = table[0]
        # Monta dict no mixin
        self.from_tables_get_ativos()


    def store_data(self):
        for btc in self.ativos:
            try:
                ativo = Ativos.objects.get(ativo=btc)
            except Exception as e:
                continue
            ativo.btc = self.ativos[btc]
            ativo.save()


class Termo(downloadMain, PdTableMixin):
    def __init__(self):
        super(Termo, self).__init__()
        self.column_data = 5
        self.link_id_form = 'filtroListaCompleta'
        self.today = (date.today() - timedelta(days=1)).strftime("%d/%m/%Y")
        self.pg_url = 'http://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/consultas/mercado-a-vista/termo/posicoes-em-aberto/'

    def download(self):
        # self.today = '09/10/2020'
        self.get_download_url()
        self.download_url = self.download_url.replace('../', '')
        self.download_url = self.b3_domain + self.download_url + '?data=%s' % (self.today)

    def get_pg_data(self):
        r = self.req_session.get(self.download_url, allow_redirects=True)
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find_all('table', attrs = {'class': 'responsive'})
        self.table_data = table[1]

        # Monta dict no mixin
        self.from_tables_get_ativos()

    def store_data(self):
        for termo in self.ativos:
            try:
                ativo = Ativos.objects.get(ativo=termo)
            except Exception as e:
                continue
            ativo.termo = self.ativos[termo]
            ativo.save()



if __name__ == "__main__":
    if sys.argv[1] == 'classif_setorial':
        classif_setorial = classifSetorial()
        #classif_setorial.download()
        classif_setorial.read_csv()
        classif_setorial.store_data()

    if sys.argv[1] == 'valor_mercado':
        valor_mercado = valorMercado()
        # valor_mercado.download()
        valor_mercado.read_csv_store_valor_mercado()

    if sys.argv[1] == 'aluguel':
        aluguel = Aluguel()
        aluguel.get_pg_data()
        aluguel.store_data()

    if sys.argv[1] == 'termo':
        termo = Termo()
        termo.download()
        termo.get_pg_data()
        termo.store_data()
