from django.db.models import QuerySet
from vjit_network.core.models import Student, Education
from typing import List, TypeVar, Generic
import pandas as pd


class StudentExport(object):
    _fields = ('username',
               'password',
               'first_name',
               'last_name',
               'email',
               'gender',
               'phone',
               'birth_date',
               'address',
               'school_name',
               'class_id',
               'student_code',
               'field_of_study',
               'start_year',
               'end_year')

    def __init__(self,
                 username: str,
                 password: str,
                 first_name: str,
                 last_name: str,
                 email: str,
                 gender: str,
                 phone: str,
                 birth_date: str,
                 address: str,
                 school_name: str,
                 class_id: str,
                 student_code: str,
                 field_of_study: str,
                 start_year: int,
                 end_year: int):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.gender = gender
        self.phone = phone
        self.birth_date = birth_date
        self.address = address
        self.school_name = school_name
        self.class_id = class_id
        self.student_code = student_code
        self.field_of_study = field_of_study
        self.start_year = start_year
        self.end_year = end_year

    def to_row(self):
        row = []
        for field in self._fields:
            row.append(getattr(self, field))
        return row


class StudentExportConvert:

    def __init__(self, export_class):
        self.export_class = export_class

    def to_xlsx(self, data):
        sheet = {}
        for field in self.export_class._fields:
            sheet[field] = []
        for row_obj in data:
            row_data = row_obj.to_row()
            for index, field in enumerate(self.export_class._fields):
                sheet[field].append(row_data[index])
        return pd.DataFrame(sheet)


def dump_student_to_xlsx(queryset: QuerySet):
    list_student = []

    for student in queryset:
        username = student.user.username
        password = None
        first_name = student.user.first_name
        last_name = student.user.last_name
        gender = student.user.gender
        email = student.user.email
        phone = student.phone
        birth_date = student.birth_date
        address = student.address

        school_name = None
        class_id = None
        student_code = None
        field_of_study = None
        start_year = None
        end_year = None

        education: Education = student.educations.first()

        if education:
            school_name = education.school_name
            class_id = education.class_id
            student_code = education.student_code
            field_of_study = education.field_of_study
            start_year = education.start_year
            end_year = education.end_year

        list_student.append(StudentExport(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            gender=gender,
            phone=phone,
            birth_date=birth_date,
            address=address,
            school_name=school_name,
            class_id=class_id,
            student_code=student_code,
            field_of_study=field_of_study,
            start_year=start_year,
            end_year=end_year
        ))

    converter = StudentExportConvert(StudentExport)
    return converter.to_xlsx(list_student)
