from django.db import models
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext as _
from django.core.validators import MinValueValidator

import os
import uuid


class UUIDPrimaryModel(models.Model):
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


class BigIntPrimary(models.Model):
    id = models.BigAutoField(primary_key=True)

    class Meta:
        abstract = True


class CreateAtModel(models.Model):
    create_at = models.DateTimeField(
        verbose_name=_('Create at'),
        auto_now_add=True
    )

    class Meta:
        abstract = True

class IsActiveModel(models.Model):
    is_active = models.BooleanField(
        verbose_name=_('Is active'),
        default=True
    )

    class Meta:
        abstract = True