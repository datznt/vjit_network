from rest_framework import serializers
from django.conf import settings

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


class OtpValidator:

    def __call__(self, value):
        if value not in range(OTP_CODE_FROM, OTP_CODE_TO):
            message = 'OTP is not valid'
            raise serializers.ValidationError(message)
