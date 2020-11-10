from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CoreConfig(AppConfig):
    name = 'vjit_network.core'
    verbose_name = _('System content')

    def ready(self):
        from vjit_network.core import signals, utils
