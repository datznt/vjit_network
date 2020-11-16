from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.views import View
from django.db.models import Sum, Count
from django.utils.timezone import datetime
from django.core.cache import cache
from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework import status
from vjit_network.core.models import User, VisitLogger, Student, Education
from vjit_network.core.forms import UserCreationForm, StudentCreationForm, EducationCreationForm
from vjit_network.core.business import lookup_groups_from_class_id, join_user_to_groups
import os
import json
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

USER_TYPES_COLORS = {'is_staff':  '#58508d',
                     'is_student': '#bc5090', 'is_company': '#ff6361'}

USER_TYPES_CHOICES = ['is_staff', 'is_student', 'is_company']


def read_file(request):
    f = open(os.path.join(settings.BASE_DIR, '.well-known',
                          'pki-validation', 'A0A183D1A0C45A0E1E7DCB87545B2C2E.txt'), 'r')
    file_content = f.read()
    f.close()
    return HttpResponse(file_content, content_type="text/plain")


class AdminDashboardView(View):
    def get(self, request, *args, **kwargs):
        dashboard_statistics = cache.get('dashboard_statistics', None)
        if not dashboard_statistics:
            traffic_statistics = self._chart_traffic_statistics()
            user_type_statistics = self._chart_user_type_statistics()
            dashboard_statistics = {
                'traffic_statistics': traffic_statistics,
                'user_type_statistics': user_type_statistics
            }
            cache.set('dashboard_statistics',
                      dashboard_statistics, 60 * 60 * 2)
        return JsonResponse({
            'charts': dashboard_statistics
        })

    def _chart_traffic_statistics(self):
        months_labels = []
        query_result = {'labels': [], 'datasets': []}
        datetime_now = datetime.now()
        for month in range(1, datetime_now.month + 1):
            month_label = '{m}/{y}'.format(m=month, y=datetime_now.year)
            months_labels.append(month_label)
        query_result['labels'] = months_labels
        for user_type in USER_TYPES_CHOICES:
            user_type_lookup = 'user__{type}'.format(type=user_type)

            query_option = {}
            query_option['date__year'] = datetime_now.year
            query_option[user_type_lookup] = True

            dataset = {'data': []}
            dataset['label'] = user_type.replace('is_', '')
            dataset['borderColor'] = USER_TYPES_COLORS[user_type]
            for month in range(1, datetime_now.month + 1):
                query_option['date__month'] = month
                qs = VisitLogger.objects.filter(
                    **query_option).aggregate(Sum('visits_count'))
                dataset['data'].append(qs['visits_count__sum'] or 0)
            query_result['datasets'].append(dataset)
        return query_result

    def _chart_user_type_statistics(self):
        query_result = {'labels': [], 'datasets': [
            {'data': [], 'backgroundColor': []}]}
        for user_type in USER_TYPES_CHOICES:
            param = {user_type: True}
            qs = User.objects.filter(**param).count()
            query_result['datasets'][0]['data'].append(qs)
            query_result['datasets'][0]['backgroundColor'].append(
                USER_TYPES_COLORS[user_type])
            query_result['labels'].append(user_type.replace('is_', ''))
        return query_result


class StudentCreateView(View):

    def post(self, request, *args, **kwargs):
        try:
            resq_data = json.loads(request.body)
        except Exception as exception:
            logger.exception(exception)
            return HttpResponseBadRequest('Data is not valid')

        try:
            user_form = UserCreationForm(resq_data.get('user', {}))
            if not user_form.is_valid():
                raise ValidationError(user_form.errors)
            user_instance: User = user_form.save()
            user_instance.update_fields(is_student=True)

            student_form = StudentCreationForm({
                **resq_data.get('student', {}),
                'user':  user_instance.pk
            })
            if not student_form.is_valid():
                raise ValidationError(student_form.errors)
            student_instance: Student = student_form.save()

            education_form = EducationCreationForm({
                **resq_data.get('education', {}),
                'student':  student_instance.pk
            })

            if not education_form.is_valid():
                raise ValidationError(education_form.errors)

            education_instance: Education = education_form.save()
            groups_need_add = lookup_groups_from_class_id(
                ['vjit'], education_instance.class_id)
            
            join_user_to_groups(user_instance, groups_need_add)

        except ValidationError as exception:
            return HttpResponseBadRequest(exception)
        except Exception as exception:
            if user_instance:
                user_instance.delete()
            logger.exception(exception)
            raise exception
        return HttpResponse(status=status.HTTP_201_CREATED)