from django.core.management.base import BaseCommand
from django.core.exceptions import ImproperlyConfigured
import logging

logger = logging.getLogger(__name__)


class LoggerCommand(BaseCommand):
    cmd_name = None

    def _get_class_name(self):
        if not self.cmd_name:
            raise ImproperlyConfigured('cmd_name is None')
        return self.cmd_name

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super(LoggerCommand, self).__init__(stdout, stderr, no_color, force_color)
        self.log_start_command()

    def log_start_command(self):
        implement_classes_name = self._get_class_name()
        logger.warning("CMD[{classes}] START".format(classes=implement_classes_name))

    def log_end_command(self):
        implement_classes_name = self._get_class_name()
        logger.warning("CMD[{classes}] END".format(classes=implement_classes_name))
