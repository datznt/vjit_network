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


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=125, required=True)

class StudentCreationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['user', 'phone', 'birth_date', 'address']
    user = forms.ModelChoiceField(User.objects.all(), required=False)


class EducationCreationForm(forms.ModelForm):

    class Meta:
        model = Education
        fields = ['student', 'school_name', 'class_id', 'student_code',
                  'field_of_study', 'start_year', 'end_year']
    student = forms.ModelChoiceField(Student.objects.all(), required=False)


class StudentUploadForm(forms.Form):
    file = forms.FileField(required=True, validators=[
        FileExtensionValidator(allowed_extensions=['xlsx'])
    ])

    def _convert_file(self, memory_file) -> pd.DataFrame:
        excel: pd.DataFrame = pd.read_excel(memory_file, keep_default_na=False)
        return excel

    def clean_file(self):
        file = self.cleaned_data['file']
        excel = self._convert_file(memory_file=file)
        if set(excel.columns) != set(StudentExport._fields):
            raise ValidationError(_('Invalid format excel'))
        self._excel = excel

    def get_user_form_row(self, row):
        return {
            'username': row.get('username', ''),
            'password': row.get('password', ''),
            'first_name': row.get('first_name', ''),
            'last_name': row.get('last_name', ''),
            'email': row.get('email', ''),
            'gender': row.get('gender', ''),
        }

    def get_student_from_row(self, row):
        birth_date = row.get('birth_date', None)
        if not pd.isna(birth_date) and hasattr(birth_date, 'date'):
            birth_date = birth_date.date()
        else:
            birth_date = ''
        return {
            'phone': str(row.get('phone', ''),),
            'birth_date': birth_date,
            'address': row.get('address', ''),
        }

    def get_education_from_row(self, row):
        return {
            'school_name': row.get('school_name', ''),
            'class_id': row.get('class_id', ''),
            'student_code': row.get('student_code', ''),
            'field_of_study': row.get('field_of_study', ''),
            'start_year': row.get('start_year', ''),
            'end_year': row.get('end_year', ''),
        }

    def get_validated(self):
        excel: pd.DataFrame = self._excel
        student_frames = []
        for index, row in excel.iterrows():
            user = self.get_user_form_row(row)
            student = self.get_student_from_row(row)
            education = self.get_education_from_row(row)

            user_form = UserCreationForm(user)
            student_form = StudentCreationForm(student)
            education_form = EducationCreationForm(education)

            user_form.is_valid()
            student_form.is_valid()
            education_form.is_valid()

            user_error = user_form.errors
            student_error = student_form.errors
            education_error = education_form.errors

            frame = {
                'objects': {
                    'user': user,
                    'student': student,
                    'education': education
                },
                'errors': {
                    'user': user_error,
                    'student': student_error,
                    'education': education_error
                }
            }
            student_frames.append(frame)

        return student_frames
