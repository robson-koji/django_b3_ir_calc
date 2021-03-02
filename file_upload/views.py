from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User, AnonymousUser
from django.views.generic.base import TemplateView
from django.core.files.base import ContentFile
from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.db.models import Q


from endorsement.views import DataEleven, DataXp, endorsement_broker
from collections import OrderedDict
from datetime import datetime, date
import os, csv

from .models import Document, get_upload_path
from .forms import DocumentForm


def redirect_view(request):
    if request.method == 'POST':
        # '/media/documents/2bsgj6idurknyuk9cdlztz7zy8z1vxg9/2020/05/13/TAEE11.SA_3W1hl3N.csv'
        path = request.POST.get('path').split('/')
        # Save file path to the user session

        # Check if user access your own files.
        # Check on session or database user field.
        if request.user.is_authenticated or path[3] == request.session.session_key:
            path = request.POST.get('path').rsplit('/', 1)[0]
            file = request.POST.get('path').split('/')[-1]

            print("\n\n\nView de redirect do Upload")
            print(path)
            print(file)

            docfile = path.split('/')
            date = "%s/%s/%s" % (docfile[4], docfile[5], docfile[6])

            request.session['path'] = path
            request.session['file'] = file
            request.session['date'] = date
            # return redirect('position')


            if '.csv' in file:
                return redirect('position')

            """
            Sempre estah convertendo o .xls para csv.
            Ver como otimizar isso. Uma possibilidade eh ver se o csv jah existe,
            mas precisa saber como identifica-lo.
            """
            try:
                # excel_to_csv(path=path, file=file)
                request.session['file'] = request.session['file'].replace('.xls', '.csv')
                return redirect('position')
            except:
                message = 'Excel to CSV conversion issue.'
                context = {'message': message}
                return render(request, 'list.html', context)

        else:
            message = 'Session expired'
            context = {'message': message}
            return render(request, 'list.html', context)


def get_session_key(request):
    if not request.user.is_authenticated:
        # Init session
        user = AnonymousUser()
        if not request.session.keys():
            request.session['anonymous'] = True
            request.session.save()
    user = request.user
    session_key = request.session.session_key
    # import pdb; pdb.set_trace()
    return (user, session_key)




def documents_home(request):
    print(f"Great! You're using Python 3.6+. If you fail here, use the right version.")
    # message = 'Upload as many files as you want!'
    message = ''

    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # Check anonymous User
            (user, session_key) = get_session_key(request)

            # File with session, to split in model
            session_file = "|%s" % (session_key)
            request.FILES['docfile'].name += session_file

            if user.is_anonymous:
                newdoc = Document(docfile=request.FILES['docfile'], user=None, session_key=session_key)
            else:
                newdoc = Document(docfile=request.FILES['docfile'], user=user, session_key=session_key)
            newdoc.save()

            return redirect('documents_home')

        else:
            message = 'The form is not valid. Fix the following error:'
    else:
        form = DocumentForm()  # An empty, unbound form

    # Load documents for the list page


    if request.user.is_anonymous:
        documents = Document.objects.filter(session_key=request.session.session_key).order_by('-id')
    else:
        documents = Document.objects.filter(Q(session_key=request.session.session_key) | Q(user=request.user) ).order_by('-id')



    # names = []
    for doc in documents:
        docfile = doc.docfile.name.split('/')
        name = docfile[-1]

        date = "%s/%s/%s" % (docfile[2], docfile[3], docfile[4])
        doc.docfile.short_name = name
        doc.docfile.date = date
        doc.docfile.csv_url = doc.docfile.url.replace('.xls', '.csv')
        # import pdb; pdb.set_trace()

    # Render list page with the documents and the form
    context = {'documents': documents, 'form': form, 'message': message}
    return render(request, 'list.html', context)


def upload_endorse_file(request):
    """ Upload 11 endorse file and store do path """

    if not '.pdf' in request.FILES['upload_endorse_file'].name:
        messages.error(request, 'Invalid file. Not PDF file extension: %s' % (request.FILES['upload_endorse_file'].name))
        return HttpResponseRedirect(reverse('endorse') +  '#upload_endorse_file')

    # import pdb; pdb.set_trace()
    eb = request.POST['optionsRadiosEndorsement']
    csv_dir = endorsement_broker[eb]['csv_dir']
    pdfs_dir = endorsement_broker[eb]['pdfs_dir']

    # Write PDF file to disk
    handle_uploaded_file(request.FILES['upload_endorse_file'], pdfs_dir) # error throws up here.

    # Call endorsement App to convert PDF to CSV
    endorsement_file = endorsement_broker[eb]['class'](csv_dir, pdfs_dir)
    csv_data = endorsement_file.get_csv_data()
    endorsement_file.store_csv(csv_data)

    if not 'endorsement_file' in request.session:
        request.session['endorsement_file'] = []
    if not request.FILES['upload_endorse_file'].name in request.session['endorsement_file']:
        request.session['endorsement_file'].append(request.FILES['upload_endorse_file'].name)
    return HttpResponseRedirect(reverse('endorse'))


def handle_uploaded_file(f, pdfs_dir):
    file_path = settings.BASE_DIR + pdfs_dir + (f.name)
    destination = open(file_path, 'wb')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()



class MergeFiles(TemplateView):
    """ O merge de dois arquivos eh feito considerando que sao dois subconjuntos de operacoes
    de um mesmo cliente de uma mesma corretora.
    Desta maneira, os arquivos refletem a mesma coisa, com a possibilidade de um ter mais
    dados que o outro, seja em data passada, ou em data recente. Nao eh possivel haver operacoes
    no meio dos arquivos, que tenham em um mes e nao em outro.
    """
    def dispatch(self, request, *args, **kwargs):
        if len(self.request.POST.getlist('merge_files')) != 2:
            return HttpResponse("Para fazer o merge devem ser selecionados dois e somente dois arquivos.")

        try:
            mf1 = self.request.POST.getlist('merge_files')[0].replace('/media/', '')
            self.f1_name = mf1.split('/')[-1]
            self.f1_first_trade, self.f1_broker_client, self.f1 = self.get_dict_from_file(self.request.POST.getlist('merge_files')[0].replace('/media/', ''))
        except:
            return HttpResponse("Erro ao abrir arquivo: %s" % (self.f1_name))

        try:
            mf2 = self.request.POST.getlist('merge_files')[1].replace('/media/', '')
            self.f2_name = mf2.split('/')[-1]
            self.f2_first_trade, self.f2_broker_client, self.f2 = self.get_dict_from_file(self.request.POST.getlist('merge_files')[1].replace('/media/', ''))
        except:
            return HttpResponse("Erro ao abrir arquivo: %s" % (self.f2_name))

        self.merge()
        self.merged_name = "%s_merged_%s.csv" % (self.f1_name.replace('.csv', ''), self.f2_name.replace('.csv', ''))

        try:
            self.save_merged()
            return redirect('documents_home')
        except:
            return HttpResponse("Erro no merge dos arquivos")




    def merge(self):
        if not self.f1_broker_client == self.f2_broker_client:
            raise ValueError('Corretora e/ou cliente são diferentes')

        f1 = self.f1
        f2 = self.f2

        # Troca file 1 com file 2, para funcionar adequadaemnte no loop abaixo.
        if self.f1_first_trade < self.f2_first_trade:
            f1 = self.f2
            f2 = self.f1

        self.merged = ','.join(self.f1_broker_client) + "\n"
        self.merged += ','.join([""] * 8) + '\n'
        for key in f1:
            if key in f2:
                if len(f1[key]) > len(f2[key]) or len(f1[key]) == len(f2[key]):
                    self.merged += f1[key]
                else:
                    self.merged += f2[key]
                del f2[key]
            else:
                self.merged += f1[key]

        # Meses em f2 que nao hah em f1.
        if f2:
            for key in f2:
                self.merged += f2[key]


    def save_merged(self):
        (user, session_key) = get_session_key(self.request)
        # File with session, to split in model
        session_file = "|%s" % (session_key)
        self.merged_name  += session_file
        merged_doc = Document()
        merged_doc.docfile.save(self.merged_name, ContentFile(self.merged))

        if user.is_anonymous:
            user = None
        else:
            user = user

        merged_doc.user=user
        merged_doc.session_key=session_key
        merged_doc.save()

    def get_dict_from_file(self, f):
        """ Get CVS data from CSV file. Dont have to convert always from PDF. """
        # import pdb; pdb.set_trace()
        try:
            out_csv =   settings.MEDIA_ROOT + f
            dict_csv = OrderedDict()

            with open(out_csv, 'r') as read_obj:
                csv_reader = csv.reader(read_obj)
                broker_client = next(csv_reader)
                next(csv_reader)

                for row in csv_reader:
                    # import pdb; pdb.set_trace()
                    ym_tuple = '%s%s' % (row[0].split('/')[2], row[0].split('/')[1])
                    if not ym_tuple in dict_csv:
                        dict_csv[ym_tuple] = ''
                    # dict_csv[ym_tuple] += ','.join(row) + '\n'

                    for e in row:
                        if ',' in e:
                            e = '"' + e + '"'
                        dict_csv[ym_tuple] += e + ','

                    dict_csv[ym_tuple] = dict_csv[ym_tuple].rstrip(',')
                    dict_csv[ym_tuple] += '\n'

                first_trade = datetime.strptime(row[0], '%d/%m/%Y').date()
            return (first_trade, broker_client, dict_csv)
        except IOError:
            raise
