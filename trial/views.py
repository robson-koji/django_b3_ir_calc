import shutil, os
from datetime import date
from django.conf import settings
from django.shortcuts import render
from django.views.generic.base import View
from django.shortcuts import redirect, render

from file_upload.views import get_session_key
from file_upload.models import Document, get_upload_path

class TrialView(View):
    def dispatch(self, request, *args, **kwargs):
        # Check anonymous User
        (user, session_key) = get_session_key(request)

        date_dir = '%s/%s/%s' % (date.today().year, date.today().month, date.today().day)
        if user.is_anonymous:
            new_dir = '%sdocuments/%s/%s' % (settings.MEDIA_ROOT,  session_key, date_dir )
            try:
                # import pdb; pdb.set_trace()
                # os.mkdir(new_dir)
                os.makedirs(new_dir, exist_ok=True)
            except FileExistsError:
                pass

            request.session['path'] = 'documents/%s/%s' % (session_key, date_dir)
            request.session['file'] = 'trial_cei_file.csv'
            request.session['date'] = date_dir

            # copy trial file to anonymous user.
            shutil.copy('/var/www/media/b3_ir_calc/try_file/trial_cei_file.csv', new_dir)
            docfile = 'documents/%s/%s/%s' % (session_key, date_dir, 'trial_cei_file.csv')
            newdoc = Document(docfile=docfile, user=None, session_key=session_key)
            newdoc.save()
            # import pdb; pdb.set_trace()
            return redirect('position')
        else:
            return redirect('documents_home')


class TrialLogoutView(View):
    def dispatch(self, request, *args, **kwargs):
        request.session.flush()
        return redirect('/')
