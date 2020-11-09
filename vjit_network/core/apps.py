from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'vjit_network.core'

    def ready(self):
        import vjit_network.core.signals
        import vjit_network.core.utils