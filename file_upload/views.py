from django.contrib.auth.models import User, AnonymousUser
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse

from .models import Document, get_upload_path
from .forms import DocumentForm

from django.conf import settings
import os



def redirect_view(request):
    if request.method == 'POST':
        # Check if user access your own files.
        # '/media/documents/2bsgj6idurknyuk9cdlztz7zy8z1vxg9/2020/05/13/TAEE11.SA_3W1hl3N.csv'
        path = request.POST.get('path').split('/')
        # Save file path to the user session
        if path[3] == request.session.session_key:
            path = request.POST.get('path').rsplit('/', 1)[0]
            file = request.POST.get('path').split('/')[-1]

            print("\n\n\nView de redirect do Upload")
            print(path)
            print(file)

            request.session['path'] = path
            request.session['file'] = file
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
    session_key = request.session.session_key
    return (user, session_key)




def my_view(request):
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

            return redirect('my-view')

        else:
            message = 'The form is not valid. Fix the following error:'
    else:
        form = DocumentForm()  # An empty, unbound form

    # Load documents for the list page
    documents = Document.objects.filter(session_key=request.session.session_key)

    # import pdb; pdb.set_trace()

    # names = []
    for doc in documents:
        docfile = doc.docfile.name.split('/')
        name = docfile[-1]

        date = "%s/%s/%s" % (docfile[2], docfile[3], docfile[4])
        doc.docfile.short_name = name
        doc.docfile.date = date
        doc.docfile.csv_url = doc.docfile.url.replace('.xls', '.csv')

    # Render list page with the documents and the form
    context = {'documents': documents, 'form': form, 'message': message}
    return render(request, 'list.html', context)


def upload_endorse_file(request):
    """ Upload 11 endorse file and store do path """

    if not '.pdf' in request.FILES['upload_endorse_file'].name:
        messages.error(request, 'Invalid file. Not PDF file extension: %s' % (request.FILES['upload_endorse_file'].name))
        return HttpResponseRedirect(reverse('endorse') +  '#upload_endorse_file')

    handle_uploaded_file(request.FILES['upload_endorse_file']) # error throws up here.
    return HttpResponseRedirect(reverse('endorse'))


def handle_uploaded_file(f):
    file_path = settings.BASE_DIR + '/recomenda_11/pdfs/%s' % (f.name)
    destination = open(file_path, 'wb')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
