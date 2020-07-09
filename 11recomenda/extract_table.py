import os, csv, glob
import pdftotext


def get_last_pdf():
    """ Pega o ultimo arquivo """
    list_of_files = glob.glob('pdfs/*') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    return (latest_file)


def pdf_2_text(tb):
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


def read_pdf(pdf_file):
    """
    Le arquivo PDF, e converte pg por pg para texto.
    Retorna lista de lista para criar arquivo CSV.
    """
    with open(pdf_file, "rb") as f:
        pdf = pdftotext.PDF(f)

    table_pages = range( 1, len(pdf)-1)

    final_data = []
    for tb in table_pages:
        list_data = pdf_2_text(pdf[tb])
        final_data.extend(list_data)

    return final_data


def store_csv(final_data):
    """ Grava arquivo CSV em disco """
    #print(*final_data, sep='\n')
    with open("csv/out.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(final_data)

pdf_file = get_last_pdf()
final_data = read_pdf(pdf_file)
store_csv(final_data)
