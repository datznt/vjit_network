from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.utils.http import urlencode
from django.db.models.query import QuerySet
from django.core.cache import cache
from rest_framework import serializers
from vjit_network.core.models import File, User
from vjit_network.api.models import NotificationTemplate, UserNotification, Notification
from urllib.parse import urlparse
from typing import List
import extraction
import requests
import random
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def get_and_authenticate_user(username, password):
    user = authenticate(username=username, password=password)
    if user is None:
        raise serializers.ValidationError(
            "Invalid username/password. Please try again!")
    return user


def create_user_account(username, email, password, first_name="",
                        last_name="", **extra_fields):
    user = User.objects.create_user(
        username=username, email=email, password=password, first_name=first_name,
        last_name=last_name, **extra_fields)
    return user


def extraction_link(url):
    html = requests.get(url).text
    parsed_uri = urlparse(url)
    extracted = extraction.Extractor().extract(html, source_url=url)
    return {
        'title': extracted.title,
        'description': extracted.description,
        'picture': extracted.image,
        'name': parsed_uri.netloc
    }


def random_range(from_num: int, to_num: int):
    return random.randint(from_num, to_num)


class NotificationBuilder:
    notification = None

    def __init__(self, actor: User, template: NotificationTemplate, recipients: List[User], payload=None, is_publish=True):
        self.actor = actor
        self.template = template
        self.recipients = recipients
        self.payload = payload
        self.is_publish = is_publish

    @classmethod
    def push(cls, actor: User, template_id: int, recipients: List[User], payload=None, is_publish=True):
        template_cache_id = cls._template_cache_id(template_id)
        template = cache.get(template_cache_id)
        if not template:
            template = NotificationTemplate.objects.get(pk=template_id)
            cache.set(template_cache_id, template, 60 * 60 * 24)
        instance = cls(actor=actor, template=template,
                       recipients=recipients, payload=payload, is_publish=is_publish)
        return instance._push_notification()

    def _push_notification(self):
        try:
            new_notification = Notification.objects.create(
                actor=self.actor, template=self.template, payload=self.payload, is_publish=is_publish)
            notification_recipients = [UserNotification(
                user=recipient, notification=new_notification) for recipient in self.recipients]
            UserNotification.objects.bulk_create(notification_recipients)
            return new_notification
        except Exception as exception:
            logger.exception(exception)
            return None

    @classmethod
    def _template_cache_id(self, template_id: str):
        return 'notify_template_' + str(template_id)
