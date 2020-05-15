from django import forms
from django.forms import ValidationError


class DocumentForm(forms.Form):
    docfile = forms.FileField(label='Upload de arquivo Excel da B3', widget=forms.FileInput(attrs={'accept': ".xls, .csv"}))

    # Validate file max size
    def clean_docfile(self):
        # import pdb; pdb.set_trace()
        docfile = self.cleaned_data.get('docfile', False)
        if docfile:
            if docfile.size > 1024*1024:
                raise ValidationError("Excel file too large ( > 1Mb )")
            return docfile
        else:
            raise ValidationError("Couldn't read uploaded Excel file")
