from django import forms
import pandas as pd


class StudentUploadForm(forms.Form):
    file = forms.FileField(required=True)

    def clean_file(self):
        file = self.cleaned_data['file']
        excel = pd.read_excel(file)
        print(excel.head())
