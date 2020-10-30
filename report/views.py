import string

from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.urls import resolve
from django.views import View

from datetime import datetime, timedelta, date
from collections import defaultdict, deque
from builtins import any as b_any

from b3_ir_calc.b3_ir_calc.ir_calc import *
from stock_price.models import StockPrice
from django_excel_csv.views import GetExcel
from b3_reference_data.models import Ativos, Setorial
from endorsement.views import DataEleven, DataXp, endorsement_broker



class ProxyView(View):
    """ Proxy class to b3_ir_calc module classes """

    # Input data from each user
    # path ='/home/robson/invest/'
    # file = 'mirae.csv'
    stock_price_file = None
    stock_detail = None

    def dispatch(self, request, *args, **kwargs):
        self.ativos = Ativos.objects.all()

        if request.session.is_empty():
            from file_upload.forms import DocumentForm
            form = DocumentForm()

            message = 'Sessão expirada. Efetue o login com o Facebook para salvar os seus arquivos B3 CEI, ou faça o upload novamente.'
            context = {'form': form, 'message': message}
            return render(request, 'list.html', context)
                # Get anonymous user data

        if not 'file' in request.session or not 'path' in request.session:
            message = {'title':'Nenhum arquivo selecionado',
                        'body':'Clique no botão abaixo para selecionar um arquivo para ver a sua posição atual.',
                        'btn_text':'Selecionar arquivo',
                        'href': 'documents_home' }
            context = {'message': message}
            return render(request, 'error.html', context)


        request.session['path'] = request.session['path'].replace('/media/', '')
        self.path = "%s%s/" % (settings.MEDIA_ROOT, request.session['path'])
        self.file = request.session['file']


        try:
            b3_tax_obj = self.handle_data(self.path, self.file)
        except FileNotFoundError:
            message = {'title': 'Arquivo não encontrado',
                        'body': 'Arquivo não encontrado: %s/%s. <br> Clique no botão abaixo para selecionar outro arquivo.' % (request.session['path'], request.session['file']) ,
                        'btn_text':'Selecionar arquivo',
                        'href': 'documents_home' }
            context = {'message': message}
            return render(request, 'error.html', context)


        # self.gather_iligal_operation(b3_tax_obj.iligal_operation)
        # import pdb; pdb.set_trace()
        self.months = self.months_reconcile(b3_tax_obj)
        self.report = self.generate_reports(self.stock_price_file, b3_tax_obj.stocks_wallet, self.months)
        # self.get_context_data()
        return super(ProxyView, self).dispatch(request, *args, **kwargs)

    def handle_data(self, path, file):
        print("\n\n\ndjango_b3_ir_calc")
        print( "ProxyView")
        print( path)
        print( file)
        # import pdb; pdb.set_trace()
        try:
            b3_tax_obj = ObjectifyData(mkt_type='VIS', path=path, file=file)
            return b3_tax_obj
        except FileNotFoundError:
            raise


    # def gather_iligal_operation(self, iligal_operation):
    #     self.iligal_operations.append(iligal_operation)

    def months_reconcile(self, b3_tax_obj):
        months = b3_tax_obj.file2object(stock_detail=self.stock_detail)
        months.month_add_detail()
        return months

    def generate_reports(self, stock_price_file, stocks_wallet, months):
        report = Report(stock_price_file, stocks_wallet, months)
        return report


class PositionView(ProxyView, TemplateView):
    """ Current position """
    template_name = "report/position.html"

    defensivas = ['BRAP4','CESP6','CPLE6','ENBR3', 'GTWR11','TAEE11','TIET11','VALE3']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # self.report.get_current_quotations()


        stocks = StockPrice.objects.all()

        # Set stock current prices.
        tmp_dict = {}
        for stock in stocks:
            """
            !!! - Para filtrar grupos de acoes.
            """
            # if stock.stock in self.defensivas:
            #     continue
            # import pdb; pdb.set_trace()
            tmp_dict[stock.stock]= {'price': str(stock.price), 'hour':stock.hour }

        self.report.current_prices = tmp_dict

        # which date to show here? Last update?
        self.curr_prices_dt = date.today()

        (self.current_position, summary) = self.report.current_position()
        context['current_position'] = self.current_position
        context['summary'] = summary
        return context


class HistoryView(ProxyView, TemplateView):
    """ History of operations """

    template_name = "report/history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['months'] = self.report.months_build_data()[0]
        context['months_operations'] = self.report.months_build_data()[1]
        return context


class HistoryDetailView(ProxyView, TemplateView):
    """ History of operations for one specific stock """
    template_name = "report/history.html"

    def dispatch(self, request, *args, **kwargs):
        self.stock_detail = kwargs['stock']
        return super(HistoryDetailView, self).dispatch(request, *args, **kwargs)


    def get_higher_values(self, val):
        """ Calculate and get the higher values of each chart element """
        for key in val:
            if key not in self.for_chart_values:
                continue
            try:
                if val[key] > self.higher_values[key]: self.higher_values[key] = val[key]
            except Exception as e:
                import pdb; pdb.set_trace()


        # if val['qt_total'] > self.higher_values['qt_total']:self.higher_values['qt_total']  = Decimal(val['qt_total'])
        # if val['avg_price'] > self.higher_values['avg_price']: self.higher_values['avg_price'] = val['avg_price']
        # if val['value'] > self.higher_values['value']: self.higher_values['value'] = val['value']
        # if val['loss'] > self.higher_values['loss']: self.higher_values['loss'] = val['loss']
        # if val['profit'] > self.higher_values['profit']: self.higher_values['profit'] = val['profit']

    def normalize_chart_values(self):
        """ Calculate and create a dict to normalize data at chart.  """
        self.normalized_chart_values = defaultdict(Decimal)
        if self.higher_values['profit'] > self.higher_values['loss']:
            self.higher_values['loss'] = self.higher_values['profit']
        else:
            self.higher_values['profit'] = self.higher_values['loss']
        max_key = max(self.higher_values, key=self.higher_values.get)
        for key, val in self.higher_values.items():
            if key in self.ignore_normalizing:
                self.normalized_chart_values[key] = 1
                continue
            if self.higher_values[key] <= 0:
                 continue
            self.normalized_chart_values[key] = str(round(self.higher_values[max_key]/self.higher_values[key], 2))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.for_chart_values = ['qt_total', 'avg_price', 'value', 'loss', 'profit', 'my_position', 'mkt_position']
        self.ignore_normalizing = ['my_position', 'mkt_position']

        self.higher_values = defaultdict(Decimal)
        bar_chart_data = defaultdict(deque)
        # Months
        for a in self.report.months_build_data()[1]:
            # One Month
            for b in self.report.months_build_data()[1][a]:
                operations_list = self.report.months_build_data()[1][a][b]
                operations_list.reverse()
                # Operations in month
                for idx, val in enumerate(  operations_list ):
                    self.get_higher_values(val)
                    # date = "%i%i%i%i" % (val['dt'].year, val['dt'].month, val['dt'].day, idx)
                    date = "%i%i%i" % (val['dt'].year, val['dt'].month, val['dt'].day)
                    for fcv in self.for_chart_values:
                        bar_chart_data[fcv].appendleft(str(val[fcv]))
                    bar_chart_data['dt'].appendleft(date)


        for k in bar_chart_data:
            if k == 'dt':
                bar_chart_data[k] = list(bar_chart_data[k])
            else:
                bar_chart_data[k] = [k] + list(bar_chart_data[k])

        self.normalize_chart_values()
        # print(self.normalized_chart_values)
        # import pdb; pdb.set_trace()

        context['bar_chart_data'] = dict(bar_chart_data)
        context['normalized_chart_values'] = dict(self.normalized_chart_values)
        context['months'] = self.report.months_build_data()[0]
        context['months_operations'] = self.report.months_build_data()[1]

        # import pdb; pdb.set_trace()
        return context

class StockPriceView(TemplateView):
    template_name = "generic/stock_price.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stocks'] = StockPrice.objects.all()
        return context



class Endorse11Download(PositionView, GetExcel):
    """
    Inherits from:
    PositionView - To merge position on data
    Get Excel - To generate csv file
    """

    template_name = "report/endorse_11.html"

    def merge(self):
        """ Merge dos dados de current_position e 11 recomenda """
        self.recomenda_11 = data_11.get_csv_from_file()
        self.current_position

        cp_endorsed = []
        for recomenda in self.recomenda_11:
            """ Check endorsed stocks against wallet stocks """
            tem_recomenda = 0
            for cp in self.current_position:
                cp_data = [ str(cp['qt']),  str(cp['buy_avg']), str(cp['curr_price']),
                            str(cp['buy_total']), str(cp['cur_total']), str(cp['balance']),
                            str(cp['balance_pct']) ]
                if cp['stock'] == recomenda[1]:
                    cp_endorsed.append( recomenda[1] )
                    recomenda += cp_data

        for cp in self.current_position:
            """ Check in wallet stocks but not endorsed """
            if not cp['stock'] in cp_endorsed:
                # print(cp['stock'])
                self.recomenda_11.append(['',cp['stock'],'','','','','','','','','','','','',
                                            str(cp['qt']),  str(cp['buy_avg']), str(cp['curr_price']),
                                                        str(cp['buy_total']), str(cp['cur_total']), str(cp['balance']),
                                                        str(cp['balance_pct'])])

    def get_column_names(self):
        # column_names = ['Companhia', 'Ticker',  '', 'Preço Atual', '', 'Preço Alvo',
        # '', 'Preço Limite', 'Recomendação',  'Risco',  'Qualidade',  'Índice',
        # 'Up/Down', '', 'Qt', 'Buy Avg',  'Curr. Price', 'Buy Total',  'Curr. Total',
        #  'Balance',  'Balance %']
        column_names = ['Companhia', 'Ticker',  'Preço Atual', 'Preço Alvo',
        'Preço Limite', 'Recomendação',  'Risco',  'Qualidade',  'Índice',
        'Up/Down', 'Mudou', 'Qt', 'Buy Avg',  'Curr. Price', 'Buy Total',  'Curr. Total',
         'Balance',  'Balance %']
        return column_names

    def get_data(self):
        ignore_columns = [2, 3, 4]
        los = []

        # Cleanup lines
        for line in self.recomenda_11:
            result_line = ''
            for idx, val in enumerate(line):
                if idx in ignore_columns:
                    line.pop(idx)
            los.append(';'.join(line))

        return los

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.merge()
        return context



class Endorse11View(PositionView):
    """
    Inherits from:
    PositionView - To merge position on data
    Get Excel - To generate csv file
    """

    template_name = "report/endorse_11.html"

    def get_btc_termo_setorial(self, papel):
        papel = papel.rstrip(string.digits)

        try:
            ativo = self.ativos.get(ativo=papel)
            setorial = ativo.setorial.get_arvore_setorial()
            return (str(ativo.get_pct_sum_btc_termo_vm()),
                    str(ativo.get_pct_btc_vm()),
                    str(ativo.get_pct_termo_vm()),
                    setorial)
        except:
            return ('','','','')

    def check_exists_in_list_get_index(self, segmento):
        if self.recomenda_xp is None:
            return ''
        segmento = segmento.replace(',', '')
        for idx, val in enumerate(self.recomenda_xp):
            if (segmento.lower() in val):
                return idx
        return 99 # high number to not dirty data.


    def merge(self):
        """ Merge dos dados de current_position, 11 recomenda, btc e termo """

        """
        !!! - Fazer um set decente para acabar com loop sobre loop
        """

        cp_endorsed = []
        for recomenda in self.recomenda_11:
            """ Check endorsed stocks against wallet stocks """
            tem_recomenda = 0
            for cp in self.current_position:
                (btc_termo_vm, btc_vm, termo_vm, setorial) = self.get_btc_termo_setorial(cp['stock'])

                segmento = setorial.split('|')[-1].lower()
                xp_top_20 = self.check_exists_in_list_get_index(segmento)

                cp_data = [ str(cp['qt']),  str(cp['buy_avg']), str(cp['curr_price']),
                            str(cp['buy_total']), str(cp['cur_total']), str(cp['balance']),
                            str(cp['balance_pct']), btc_termo_vm, btc_vm, termo_vm, setorial, str(xp_top_20) ]
                if cp['stock'] == recomenda[1]:
                    cp_endorsed.append( recomenda[1] )
                    recomenda += cp_data
                    tem_recomenda = 1
                    continue

            if not tem_recomenda:
                (btc_termo_vm, btc_vm, termo_vm, setorial) = self.get_btc_termo_setorial(recomenda[1])
                segmento = setorial.split('|')[-1]
                xp_top_20 = self.check_exists_in_list_get_index(segmento)
                recomenda += [ '', '', '', '', '', '', '',
                                btc_termo_vm, btc_vm, termo_vm, setorial, str(xp_top_20) ]



        for cp in self.current_position:
            """ Check in wallet stocks but not endorsed """
            # import pdb; pdb.set_trace()
            (btc_termo_vm, btc_vm, termo_vm, setorial) = self.get_btc_termo_setorial(cp['stock'])
            if not cp['stock'] in cp_endorsed:
                # print(cp['stock'])
                self.recomenda_11.append(['',cp['stock'],'','','','','','','','','','','','',
                                            str(cp['qt']),  str(cp['buy_avg']), str(cp['curr_price']),
                                                        str(cp['buy_total']), str(cp['cur_total']),
                                                        str(cp['balance']), str(cp['balance_pct']),
                                                        btc_termo_vm, btc_vm, termo_vm, setorial])


    def clean_data(self):
        ignore_columns = [2, 3, 4]
        # Cleanup lines
        for line in self.recomenda_11:
            result_line = ''
            for idx, val in enumerate(line):
                if idx in ignore_columns:
                    line.pop(idx)
                line[idx] = line[idx].replace(',', '.')



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        csv_dir_eleven = endorsement_broker['eleven']['csv_dir']
        pdfs_dir_eleven = endorsement_broker['eleven']['pdfs_dir']

        endorsement_file_11 = endorsement_broker['eleven']['class'](csv_dir_eleven, pdfs_dir_eleven)
        self.recomenda_11 = endorsement_file_11.get_csv_from_file()


        csv_dir_xp = endorsement_broker['xp']['csv_dir']
        pdfs_dir_xp = endorsement_broker['xp']['pdfs_dir']

        endorsement_file_xp = endorsement_broker['xp']['class'](csv_dir_xp, pdfs_dir_xp)
        self.recomenda_xp = endorsement_file_xp.get_csv_data()

        # import pdb; pdb.set_trace()

        # import pdb; pdb.set_trace()
        if not self.recomenda_11:
            return

        self.merge()
        self.clean_data()
        context['data'] = self.recomenda_11

        """
        Technical Analysis page uses exactly same data from
        Endorsement page. Only changes the template
        """
        if resolve(self.request.path_info).url_name == 'tech_analysis':
            # import pdb; pdb.set_trace()
            self.template_name = "report/tech_analysis.html"
        return context
