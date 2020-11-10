from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

from vjit_network.core.business import StudentExport

import pandas as pd


class StudentUploadForm(forms.Form):
    file = forms.FileField(required=True, validators=[
        FileExtensionValidator(allowed_extensions=['xlsx'])
    ])

    def _convert_file(self, memory_file) -> pd.DataFrame:
        excel: pd.DataFrame = pd.read_excel(memory_file)
        return excel

    def clean_file(self):
        file = self.cleaned_data['file']
        excel = self._convert_file(memory_file=file)
        if set(excel.columns) != set(StudentExport._fields):
            raise ValidationError(_('Invalid format excel'))
        self._excel = excel

    def save(self):
        excel: pd.DataFrame = self._excel
        students = []
        for index, row in excel.iterrows():
            student = StudentExport(
                username=row.get('username'),
                password=row.get('password'),
                first_name=row.get('first_name'),
                last_name=row.get('last_name'),
                email=row.get('email'),
                school_name=row.get('school_name'),
                class_id=row.get('class_id'),
                student_code=row.get('student_code'),
                field_of_study=row.get('field_of_study'),
                start_year=row.get('start_year'),
                end_year=row.get('end_year')
            )
            students.append(student)
        