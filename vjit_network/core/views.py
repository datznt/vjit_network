from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views import View
from django.db.models import Sum, Count
from django.utils.timezone import datetime
from django.core.cache import cache
from vjit_network.core import models
import os


USER_TYPES_COLORS = {'is_staff':  '#58508d',
                     'is_student': '#bc5090', 'is_company': '#ff6361'}

USER_TYPES_CHOICES = ['is_staff', 'is_student', 'is_company']


def read_file(request):
    f = open(os.path.join(settings.BASE_DIR, '.well-known',
                          'pki-validation', 'A1F0193986BD8F1AD1188A7DBED26B72.txt'), 'r')
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
            cache.set('dashboard_statistics', dashboard_statistics, 60 * 60 * 24)
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
                qs = models.VisitLogger.objects.filter(
                    **query_option).aggregate(Sum('visits_count'))
                dataset['data'].append(qs['visits_count__sum'] or 0)
            query_result['datasets'].append(dataset)
        return query_result

    def _chart_user_type_statistics(self):
        query_result = {'labels': [], 'datasets': [
            {'data': [], 'backgroundColor': []}]}
        for user_type in USER_TYPES_CHOICES:
            param = {user_type: True}
            qs = models.User.objects.filter(**param).count()
            query_result['datasets'][0]['data'].append(qs)
            query_result['datasets'][0]['backgroundColor'].append(
                USER_TYPES_COLORS[user_type])
            query_result['labels'].append(user_type.replace('is_', ''))
        return query_result
