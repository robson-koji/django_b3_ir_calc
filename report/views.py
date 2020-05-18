from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from b3_ir_calc.ir_calc import *
from django.conf import settings



class ProxyView(View):
    """ Proxy class to b3_ir_calc module classes """

    # Input data from each user
    # path ='/home/robson/invest/'
    # file = 'mirae.csv'
    stock_price_file = '/var/tmp/stock_price.json'

    def dispatch(self, request, *args, **kwargs):
        # Get anonymous user data
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
        self.report.get_current_quotations()
        (current_position, summary) = self.report.current_position()
        context['current_position'] = current_position
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
