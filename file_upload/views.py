from django.shortcuts import redirect, render
from .models import Document
from .forms import DocumentForm

from b3_ir_calc.b3excel2csv import excel_to_csv



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
                excel_to_csv(path=path, file=file)
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

def my_view(request):
    print(f"Great! You're using Python 3.6+. If you fail here, use the right version.")
    # message = 'Upload as many files as you want!'
    message = ''
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            """
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()
            """
            # File with session, to split in model
            request.session['anonymous'] = True
            session_key = request.session.session_key
            session_file = "|%s" % (session_key)
            request.FILES['docfile'].name += session_file
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()
            # """
            # Redirect to the document list after POST
            return redirect('my-view')

        else:
            message = 'The form is not valid. Fix the following error:'
    else:
        form = DocumentForm()  # An empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # names = []
    for doc in documents:
        docfile = doc.docfile.name.split('/')
        name = docfile[-1]

        date = "%s/%s/%s" % (docfile[2], docfile[3], docfile[4])

        doc.docfile.short_name = name
        doc.docfile.date = date
        doc.docfile.csv_url = doc.docfile.url.replace('.xls', '.csv')
        #doc.docfile.short_name = name
        # names.append(name)
        # import pdb; pdb.set_trace()


    # Render list page with the documents and the form
    context = {'documents': documents, 'form': form, 'message': message}
    return render(request, 'list.html', context)
