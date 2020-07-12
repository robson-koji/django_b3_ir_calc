from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.views import View

from datetime import datetime, timedelta, date

from b3_ir_calc.b3_ir_calc.ir_calc import *
from recomenda_11 import extract_table
from stock_price.models import StockPrice
from django_excel_csv.views import GetExcel



class ProxyView(View):
    """ Proxy class to b3_ir_calc module classes """

    # Input data from each user
    # path ='/home/robson/invest/'
    # file = 'mirae.csv'
    stock_price_file = None

    def dispatch(self, request, *args, **kwargs):
        # import pdb; pdb.set_trace()
        if request.session.is_empty():
            from file_upload.forms import DocumentForm
            form = DocumentForm()

            message = 'Sessão expirada. Efetue o login com o Facebook para salvar os seus arquivos B3 CEI, ou faça o upload novamente.'
            context = {'form': form, 'message': message}
            return render(request, 'list.html', context)
                # Get anonymous user data

        # import pdb; pdb.set_trace()
        request.session['path'] = request.session['path'].replace('/media/', '')
        self.path = "%s%s/" % (settings.MEDIA_ROOT, request.session['path'])
        self.file = request.session['file']

        b3_tax_obj = self.handle_data(self.path, self.file)
        # self.gather_iligal_operation(b3_tax_obj.iligal_operation)
        self.months = self.months_reconcile(b3_tax_obj)
        self.report = self.generate_reports(self.stock_price_file, b3_tax_obj.stocks_wallet, self.months)
        self.get_context_data()
        return super(ProxyView, self).dispatch(request, *args, **kwargs)

    def handle_data(self, path, file):
        print("\n\n\ndjango_b3_ir_calc")
        print( "ProxyView")
        print( path)
        print( file)
        b3_tax_obj = ObjectifyData(mkt_type='VIS', path=path, file=file)
        return b3_tax_obj

    # def gather_iligal_operation(self, iligal_operation):
    #     self.iligal_operations.append(iligal_operation)

    def months_reconcile(self, b3_tax_obj):
        months = b3_tax_obj.file2object()
        months.month_add_detail()
        return months

    def generate_reports(self, stock_price_file, stocks_wallet, months):
        report = Report(stock_price_file, stocks_wallet, months)
        return report


class PositionView(ProxyView, TemplateView):
    """ Current position """
    template_name = "report/position.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # self.report.get_current_quotations()


        stocks = StockPrice.objects.all()

        # Set stock current prices.
        tmp_dict = {}
        for stock in stocks:
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


class StockPriceView(TemplateView):
    stock_price_file = '/var/tmp/stock_price.json'
    template_name = "generic/stock_price.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with open(self.stock_price_file, 'r') as f:
            stock_price_file = json.load(f)
            context['date'] = list(stock_price_file)[0]
            context['values'] = stock_price_file[context['date']]

        return context



class Endorse_11(PositionView, GetExcel):
    """ History of operations """

    template_name = "report/endorse_11.html"

    def merge(self):
        """ Merge dos dados de current_position e 11 recomenda """
        self.recomenda_11 = extract_table.get_csv_data()
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
        column_names = ['Companhia', 'Ticker',  '', 'Preço Atual', '', 'Preço Alvo',
        '', 'Preço Limite', 'Recomendação',  'Risco',  'Qualidade',  'Índice',
        'Up/Down', '', 'Qt', 'Buy Avg',  'Curr. Price', 'Buy Total',  'Curr. Total',
         'Balance',  'Balance %']
        return column_names

    def get_data(self):
        los = [';'.join(x) for x in self.recomenda_11]
        return los


        # import pdb; pdb.set_trace()
        # return map(''.join, self.recomenda_11)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.merge()

        # import pdb; pdb.set_trace()
        # self.recomenda_11
        # get_column_names(column_names)
        # get_data(map(''.join, self.recomenda_11)


        # context['months'] = self.report.months_build_data()[0]
        # context['months_operations'] = self.report.months_build_data()[1]
        return context
