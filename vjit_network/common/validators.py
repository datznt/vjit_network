from rest_framework import serializers
from django.conf import settings
from django.utils.deconstruct import deconstructible
from django.core.validators import ValidationError
from django.utils.translation import gettext_lazy as _

OTP_CODE_FROM = settings.OTP_CODE_FROM
OTP_CODE_TO = settings.OTP_CODE_TO


class MaxValueValidator:
    def __init__(self, base):
        self.base = base

    def __call__(self, value):
        if value > self.base:
            message = 'Value cannot be more than %d.' % self.base
            raise serializers.ValidationError(message)


class MinValueValidator:
    def __init__(self, base):
        self.base = base

    def __call__(self, value):
        if value < self.base:
            message = 'Value cannot be less than %d.' % self.base
            raise serializers.ValidationError(message)


@deconstructible
class OtpValidator:
    def __call__(self, value):
        if value not in range(OTP_CODE_FROM, OTP_CODE_TO):
            message = 'OTP is not valid'
            raise serializers.ValidationError(message)


@deconstructible
class FileMaxSizeValidator:
    message = _(
        'File size is too %(max_size)s'
    )
    code = 'invalid_size'

    def __init__(self, max_size=None, message=None, code=None):
        self.max_size = max_size
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        file_size = value.size
        if self.max_size is not None and file_size > self.max_size:
            raise ValidationError(
                self.message, code=self.code, params={
                    'max_size': self.verbose_size(), }
            )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.max_size == other.max_size and
            self.message == other.message and
            self.code == other.code
        )

    def verbose_size(self):
        return f'{int(self.max_size / (1024*1024))}MB'
