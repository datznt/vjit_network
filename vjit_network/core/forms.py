# from dal import autocomplete
from django import forms

from vjit_network.core import models

import pandas as pd


class StudentUploadForm(forms.Form):
    file = forms.FileField(required=True)

    def clean_file(self):
        file = self.cleaned_data['file']
        excel = pd.read_excel(file)
        print(excel.head())
