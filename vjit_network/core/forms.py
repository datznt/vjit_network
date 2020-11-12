from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

from vjit_network.core.business import StudentExport
from vjit_network.core.models import User, Student, Education

import pandas as pd
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

UserBaseForm = forms.modelform_factory(
    model=User,
    fields=['username', 'first_name', 'last_name', 'email', 'password']
)

StudentBaseForm = forms.modelform_factory(
    model=Student,
    fields=['user', 'phone', 'birth_date', 'address']
)

EducationBaseForm = forms.modelform_factory(
    model=Education,
    fields=['student','school_name', 'class_id', 'student_code',
            'field_of_study', 'start_year', 'end_year']
)


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

        error_list, success_list = [], []
        for index, row in excel.iterrows():

            user_form = UserBaseForm({
                'username': row.get('username'),
                'password': row.get('password'),
                'first_name': row.get('first_name'),
                'last_name': row.get('last_name'),
                'email': row.get('email'),
                'gender': row.get('gender'),
                'is_student': True
            })

            if not user_form.is_valid():
                raise user_form.errors

            user: User = user_form.save()

            student_form = StudentBaseForm({
                'user': user.pk,
                'phone': str(row.get('phone')),
                'birth_date': row.get('birth_date'),
                'address': row.get('address'),
            })

            if not student_form.is_valid():
                raise student_form.errors

            try:
                student: Student = student_form.save()
            except Exception as create_student_exception:
                logger.exception(create_student_exception)
                student.delete()
                continue

            education_form = EducationBaseForm({
                'student': student.pk,
                'school_name': row.get('school_name'),
                'class_id': row.get('class_id'),
                'student_code': row.get('student_code'),
                'field_of_study': row.get('field_of_study'),
                'start_year': row.get('start_year'),
                'end_year': row.get('end_year')
            })

            if not education_form.is_valid():
                raise education_form.errors

            try:
                education: Education = education_form.save()
            except Exception as create_education_exception:
                logger.exception(create_education_exception)
                student.delete()
                continue
