from django.contrib.auth.models import User, AnonymousUser
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q

from .models import Document, get_upload_path
from .forms import DocumentForm

from django.conf import settings
from endorsement.views import DataEleven, DataXp, endorsement_broker
import os



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
        documents = Document.objects.filter(session_key=request.session.session_key)
    else:
        documents = Document.objects.filter(Q(session_key=request.session.session_key) | Q(user=request.user) )



    # names = []
    for doc in documents:
        docfile = doc.docfile.name.split('/')
        name = docfile[-1]

        date = "%s/%s/%s" % (docfile[2], docfile[3], docfile[4])
        doc.docfile.short_name = name
        doc.docfile.date = date
        doc.docfile.csv_url = doc.docfile.url.replace('.xls', '.csv')

    # Render list page with the documents and the form
    #import pdb; pdb.set_trace()
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
    request.session['endorsement_file'].append(request.FILES['upload_endorse_file'].name)
    return HttpResponseRedirect(reverse('endorse'))


def handle_uploaded_file(f, pdfs_dir):
    file_path = settings.BASE_DIR + pdfs_dir + (f.name)
    destination = open(file_path, 'wb')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
