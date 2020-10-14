from collections import defaultdict
from zipfile import ZipFile
from bs4 import BeautifulSoup
from urllib.parse import urlparse

import requests, re, sys
import pandas as pd


class downloadMain():
    def __init__(self):
        self.req_session = requests.Session()
        # Find download_url by id or text. Depends on page layout.
        self.link_text_to_find = ''
        self.link_id = ''
        self.files_dir_path = 'files'
        self.b3_domain = 'http://b3.com.br/'

    def get_download_url(self):
        r = self.req_session.get(self.pg_url)
        soup = BeautifulSoup(r.content, 'html.parser')

        if self.link_id:
            self.download_url = soup.find_all('a', attrs = {'id': self.link_id})[0].get('href')

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
        zipped_archive = self.files_dir_path + "/%s" % (self.filename)
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
        self.file = 'files/Setorial B3 05-10-2020 (português).xlsx'
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
                    setores[setor][subsetor][segmento].append(row[3])
                except Exception as e:
                    print(e)
                    import pdb; pdb.set_trace()
            elif pd.isna(row[2]):
                setor = subsetor = segmento = ''



        print(setores)
        # import pdb; pdb.set_trace()




class valorMercado(downloadMain):
    def __init__(self):
        super(valorMercado, self).__init__()
        self.pg_url = 'http://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/consultas/mercado-a-vista/valor-de-mercado-das-empresas-listadas/bolsa-de-valores/'
        self.link_text_to_find = 'Histórico diário'

    def download(self):
        self.get_download_url()
        self.response = self.req_session.get(self.download_url, allow_redirects=True)
        self.get_filename_from_url()
        self.file = self.files_dir_path + "/%s" % (self.filename)
        open(self.file, 'wb').write(self.response.content)


if __name__ == "__main__":
    if sys.argv[1] == 'classif_setorial':
        classif_setorial = classifSetorial()
        #classif_setorial.download()
        classif_setorial.read_csv()

    if sys.argv[1] == 'valor_mercado':
        valor_mercado = valorMercado()
        valor_mercado.download()
