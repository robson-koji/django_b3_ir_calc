import os, re, csv, glob
import pdftotext
from django.conf import settings

BASE_DIR = settings.BASE_DIR


class EndorsementFile():
    def __init__(self, csv_dir, pdfs_dir):
        self.csv_dir = csv_dir
        self.pdfs_dir = pdfs_dir

    def pdf_2_text(self, tb):
        raise NotImplementedError

    def read_pdf(self, pdf_file):
        raise NotImplementedError

    def get_last_pdf(self):
        """ Pega o ultimo arquivo """
        pdfs_dir = BASE_DIR + self.pdfs_dir + '*'
        list_of_files = glob.glob(pdfs_dir) # * means all if need specific format then *.csv
        try:
            latest_file = max(list_of_files, key=os.path.getctime)
        except:
            latest_file = None
        return (latest_file)

    def store_csv(self, final_data):
        """ Grava arquivo CSV em disco """
        #print(*final_data, sep='\n')
        csv_path = BASE_DIR + self.csv_dir + 'out.csv'
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(final_data)

    def get_csv_data(self):
        """ Always convert CSV from PDF. """
        pdf_file = self.get_last_pdf()
        if pdf_file is not None:
            final_data = self.read_pdf(pdf_file)
            return final_data

    def get_csv_from_file(self):
        """ Get CVS data from CSV file. Dont have to convert always from PDF. """
        # import pdb; pdb.set_trace()
        try:
            out_csv =  BASE_DIR + self.csv_dir + 'out.csv'
            with open(out_csv, 'r') as read_obj:
                csv_reader = csv.reader(read_obj)
                list_of_rows = list(csv_reader)
            return list_of_rows
        except FileNotFoundError:
            return None

class DataXp(EndorsementFile):
    def read_pdf(self, pdf_file):
        """
        Le arquivo PDF, e lista de prioridade de setores ordenados.

        """
        with open(pdf_file, "rb") as f:
            pdf = pdftotext.PDF(f)

            # import pdb; pdb.set_trace()
            final_data = []
            for pg in pdf:
                if 'Top 20' in pg:
                    lines = pg.split('\n')
                    ignore = True
                    for line in lines:
                        if ignore and not 'Top 20' in line:
                            continue
                        if line == '':
                            continue
                        elif 'Disclaimer:' in line:
                            ignore = True
                        else:
                            ignore = False
                            try:
                                sector = (line.split('  ')[1]).lower()
                                if sector: final_data.append(sector)
                                if sector == '':
                                    sector = (line.split('  ')[0]).lower()
                                    if sector: final_data.append(sector)
                            except:
                                continue
        return final_data

class DataEleven(EndorsementFile):
    def pdf_2_text(self, tb):
        """
        Recebe uma pg em PDF com uma tabela e retorna uma lista.
        Cada linha da tabela eh uma string na lista.
        """
        list_data = []
        for line in tb.splitlines():
            dict_line = {'alerta':'', 'data':[]}
            if not '$' in line:
                continue

            if '>>' in line:
                dict_line['alerta'] += ' >> '
                line = line.replace('>>', '')
            if '<<' in line:
                dict_line['alerta'] += ' << '
                line = line.replace('<<', '')
            if '##' in line:
                dict_line['alerta'] += ' ## '
                line = line.replace('##', '')

            line = line.replace('%', '')


            line_split = line.split()
            line_split.reverse()

            if line_split[5] == '-':
                line_split.insert( 6, '-')

            nome = ''
            for idx in range(len(line_split)):
                if idx <= 11:
                    dict_line['data'].append(line_split[idx])
                else:
                    nome = line_split[idx] + ' ' + nome

            dict_line['data'].append(nome)
            dict_line['data'].reverse()
            dict_line['data'].append(dict_line['alerta'])
            list_data.append(dict_line['data'])

        #print(*list_data, sep='\n')

        return list_data


    def read_pdf(self, pdf_file):
        """
        Le arquivo PDF, e converte pg por pg para texto.
        Retorna lista de lista para criar arquivo CSV.
        """
        with open(pdf_file, "rb") as f:
            pdf = pdftotext.PDF(f)

        table_pages = range( 1, len(pdf)-1)

        final_data = []
        for tb in table_pages:
            list_data = self.pdf_2_text(pdf[tb])
            final_data.extend(list_data)

        return final_data


endorsement_broker = {
                    'xp':{
                        'pdfs_dir':'/endorsement/data_xp/pdfs/',
                        'csv_dir':'/endorsement/data_xp/csv/',
                        'class':DataXp,
                        },
                    'eleven':{
                        'pdfs_dir':'/endorsement/data_11/pdfs/',
                        'csv_dir':'/endorsement/data_11/csv/',
                        'class':DataEleven,
                        }
                    }

if __name__ == '__main__':
    final_data = get_csv_data()
    store_csv(final_data)
