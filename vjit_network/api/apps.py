from django.apps import AppConfig
from django.conf import settings

class ApiConfig(AppConfig):
    name = 'vjit_network.api'

    def ready(self):
        from vjit_network.api import signals