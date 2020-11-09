import os
import uuid

from django.db import models
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext as _
from django.core.validators import MinValueValidator

class UUIDPrimaryKeyModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    class Meta:
        abstract = True


class PerfectModel(models.Model):
    class Meta:
        abstract = True

    def update_fields(self, **kwargs):
        update_fields = []
        for k, v in kwargs.items():
            setattr(self, k, v)
            update_fields.append(k)
        self.save(update_fields=update_fields)