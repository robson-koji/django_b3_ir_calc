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
from reference_data.models import *
from endorsement.views import DataEleven, DataXp, endorsement_broker
from corporate_events.views import CorporateEventView


class ProxyView(View):
    """ Proxy class to b3_ir_calc module classes """

    # Input data from each user
    # path ='/home/robson/invest/'
    # file = 'mirae.csv'
    stock_price_file = None
    stock_detail = None
    broker = None

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

        self.get_broker()
        self.get_corporate_events()

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


        # Pass two functions to ObjectifyData
        # self.broker_taxes = self.get_broker_taxes()
        # self.b3_taxes = self.get_b3_taxes()

        return super(ProxyView, self).dispatch(request, *args, **kwargs)

    def handle_data(self, path, file):
        print("\n\n\ndjango_b3_ir_calc")
        print( "ProxyView")
        print( path)
        print( file)
        # import pdb; pdb.set_trace()
        try:
            b3_tax_obj = ObjectifyData(mkt_type='VIS', path=path, file=file, \
                                        broker_taxes=self.get_broker_taxes(), \
                                        b3_taxes=self.get_b3_taxes(), \
                                        corporate_events=CorporateEventView)
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

    def get_broker(self):
        """ Get broker from self.file """
        self.broker = Broker.objects.get(id=1)

    def get_broker_taxes(self):
        """ return function bellow to b3_ir_calc """
        def broker_taxes(date):
            """ Function returned.
            Multiple operation value against this function to get b3 taxes. """
            return self.broker.get_broker_taxes(date)
        return broker_taxes

    def get_b3_taxes(self):
        """ return function bellow to b3_ir_calc """
        def b3_taxes(date):
            """ Function returned.
            Multiple operation value against this function to get b3 taxes. """
            return B3Taxes.get_b3_taxes(date)
        return b3_taxes

    def get_corporate_events(self):
        cev = CorporateEventView()
        self.cev = cev.corporate_events



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


class LastZeroedStocks(ProxyView, TemplateView):
    """ History of operations """

    template_name = "report/last_zeroed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['months'] = self.report.months_build_data()[0]
        #context['months_operations'] = self.report.months_build_data()[1]

        zeroed_stocks = defaultdict(bool)
        months_operations = self.report.months_build_data()[1]

        last_months = list(months_operations.keys())[0:3]
        dt_end =  date.today() - timedelta(days=5)
        dt_start =  date.today() - timedelta(days=45)
        last_months.reverse()
        for month in last_months:
            # print(month)
            for idx, asset in months_operations[month].items():
                for oper in asset:
                    if oper['dt'] > dt_start and oper['dt'] < dt_end:
                        if oper['qt_total'] == 0 :
                            zeroed_stocks[oper['name']] = True
                        else:
                            zeroed_stocks[oper['name']] = False
                        # import pdb; pdb.set_trace()

            # print(zeroed_stocks)
            # import pdb; pdb.set_trace()

        context['zeroed_stocks'] = dict(zeroed_stocks)



        # import pdb; pdb.set_trace()
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
        self.stock_detail = kwargs['stock'].upper()
        return super(HistoryDetailView, self).dispatch(request, *args, **kwargs)


    def get_higher_values(self, val):
        """ Calculate and get the higher values of each chart element """
        # import pdb; pdb.set_trace()

        for key in dir(val):

        # for key in val:
            if key not in self.for_chart_values:
                continue
            try:
                if getattr(val, key) > self.higher_values[key]: self.higher_values[key] = getattr(val, key)
            except Exception as e:
                print (e)
                import pdb; pdb.set_trace()

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

    def today_position(self, bar_chart_data):
        # Se for o caso, implementar essa def no b3_ir_calc.
        # Add today data to forecast real postion or last sold position.
        # Dupĺicate last elements
        # bar_chart_data[k].append(bar_chart_data[k][-1])
        # Update last elements
        today = "%i/%s - %s" % (date.today().day, date.today().strftime('%b'), 'Projection')
        today_price = StockPrice.objects.get(stock=self.stock_detail).price
        if int(bar_chart_data['qt_total'][-1]) == 0:
            qt_total = int(bar_chart_data['qt_total'][-2])
        else:
            qt_total = int(bar_chart_data['qt_total'][-1])
        my_position =  qt_total * Decimal(bar_chart_data['avg_price'][-1])
        mkt_position = qt_total * today_price

        chk_higher_values = {'dt':today, 'qt_total':qt_total,'unit_price':today_price,
                            'my_position':my_position, 'mkt_position':mkt_position,
                            'value':0, 'avg_price':0}

        bar_chart_data['dt'].append(today)
        bar_chart_data['qt_total'].append(bar_chart_data['qt_total'][-1])
        bar_chart_data['unit_price'].append(str(today_price))
        bar_chart_data['my_position'].append(str(my_position))
        bar_chart_data['mkt_position'].append(str(mkt_position))
        profit_loss = mkt_position - my_position
        if profit_loss > 0:
            bar_chart_data['profit'].append(str(profit_loss))
            bar_chart_data['loss'].append(0)
            chk_higher_values['profit'] = profit_loss
            chk_higher_values['loss'] = 0
        else:
            bar_chart_data['loss'].append(str(profit_loss * -1))
            bar_chart_data['profit'].append(0)
            chk_higher_values['loss'] = profit_loss
            chk_higher_values['profit'] = 0
        bar_chart_data['value'].append(0)
        bar_chart_data['avg_price'].append(bar_chart_data['avg_price'][-1])
        bar_chart_data['balance'].append(str(profit_loss))
        chk_higher_values['balance'] = profit_loss

        # bar_chart_data['avg_price'].append(bar_chart_data['avg_price'][-1])
        self.get_higher_values(chk_higher_values)



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.for_chart_values = ['qt_total', 'avg_price', 'value', 'loss', 'profit', 'my_position', 'mkt_position', 'unit_price', 'balance']
        self.ignore_normalizing = ['my_position', 'mkt_position', 'balance']

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

                    dt = "%i/%s" % (val.dt.day, val.dt.strftime('%b'))
                    for fcv in self.for_chart_values:
                        try:
                            #bar_chart_data[fcv].appendleft(str(val[fcv]))
                            bar_chart_data[fcv].appendleft(str(getattr(val, fcv)))
                            balance = val.mkt_position - val.my_position
                        except:
                            # import pdb; pdb.set_trace()
                            continue

                    bar_chart_data['dt'].appendleft(dt)
                    bar_chart_data['balance'].appendleft(str(balance))
                    val.balance = balance
                    self.get_higher_values(val)

        for k in bar_chart_data:
            if k == 'dt':
                bar_chart_data[k] = list(bar_chart_data[k])
            else:
                bar_chart_data[k] = [k] + list(bar_chart_data[k])

        self.today_position(bar_chart_data)
        self.normalize_chart_values()

        context['show_chart'] = True

        corporate_events = self.cev.values_list('asset__ativo', flat=True)
        if re.sub('\d', '', self.stock_detail) in corporate_events:
            months_keys = list(self.report.months_build_data()[1].keys())
            # import pdb; pdb.set_trace()
            if len(months_keys) == 1 and \
                len(self.report.months_build_data()[1][months_keys[0]][self.stock_detail])==1 :
                    context['show_chart'] = False

        context['bar_chart_data'] = dict(bar_chart_data)
        context['normalized_chart_values'] = dict(self.normalized_chart_values)
        context['months'] = self.report.months_build_data()[0]
        context['months_operations'] = self.report.months_build_data()[1]
        context['stock_detail'] = self.stock_detail
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
                if cp['stock'] == recomenda:
                    cp_endorsed.append( recomenda )
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
            # import pdb; pdb.set_trace()
            setorial = ativo.setorial.get_arvore_setorial()
            # import pdb; pdb.set_trace()
            indices = '  '.join([str(i) for i in ativo.indice.all()])
            # import pdb; pdb.set_trace()
            return (indices,
                    str(ativo.get_pct_sum_btc_termo_vm()),
                    str(ativo.get_pct_btc_vm()),
                    str(ativo.get_pct_termo_vm()),
                    setorial)
        except:
            return ('','','','','')

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
        # for recomenda in self.recomenda_11:
        #     # import pdb; pdb.set_trace()
        #     """ Check endorsed stocks against wallet stocks """
        tem_recomenda = 0
        for cp in self.current_position:
            (indices, btc_termo_vm, btc_vm, termo_vm, setorial) = self.get_btc_termo_setorial(cp['stock'])

            segmento = setorial.split('|')[-1].lower()
            xp_top_20 = self.check_exists_in_list_get_index(segmento)

            cp_data = [ str(cp['qt']),  str(cp['buy_avg']), str(cp['curr_price']),
                        str(cp['buy_total']), str(cp['cur_total']), str(cp['balance']),
                        str(cp['balance_pct']), btc_termo_vm, btc_vm, termo_vm, setorial, indices ]
            if cp['stock'] in self.recomenda_11:
                cp_endorsed.append( cp['stock'] )
                self.recomenda_11[cp['stock']] += cp_data
                tem_recomenda = 1
                continue
            else:
                """ Check in wallet stocks but not endorsed """
                self.recomenda_11[cp['stock']] = ['',cp['stock'],'','','','','','','','','','','','',
                                            str(cp['qt']),  str(cp['buy_avg']), str(cp['curr_price']),
                                                        str(cp['buy_total']), str(cp['cur_total']),
                                                        str(cp['balance']), str(cp['balance_pct']),
                                                        btc_termo_vm, btc_vm, termo_vm, setorial, indices]

        for recomenda in self.recomenda_11:
            if not recomenda in cp_endorsed:
                (indices, btc_termo_vm, btc_vm, termo_vm, setorial) = self.get_btc_termo_setorial(recomenda)
                segmento = setorial.split('|')[-1]
                xp_top_20 = self.check_exists_in_list_get_index(segmento)
                self.recomenda_11[recomenda] += [ '', '', '', '', '', '', '',
                                btc_termo_vm, btc_vm, termo_vm, setorial, indices ]


    def clean_data(self):
        ignore_columns = [2, 3, 4]
        # Cleanup lines
        for key in self.recomenda_11:
            result_line = ''
            for idx, val in enumerate(self.recomenda_11[key]):
                if idx in ignore_columns:
                    self.recomenda_11[key].pop(idx)
                self.recomenda_11[key][idx] = self.recomenda_11[key][idx].replace(',', '.')



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        csv_dir_eleven = endorsement_broker['eleven']['csv_dir']
        pdfs_dir_eleven = endorsement_broker['eleven']['pdfs_dir']

        endorsement_file_11 = endorsement_broker['eleven']['class'](csv_dir_eleven, pdfs_dir_eleven)
        self.recomenda_11 = endorsement_file_11.get_dict_from_file()


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
