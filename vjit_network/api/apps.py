from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class ApiConfig(AppConfig):
    name = 'vjit_network.api'
    verbose_name = _('System API')

    def ready(self):
        from vjit_network.api import signals
