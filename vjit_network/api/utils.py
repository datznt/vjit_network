from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.utils.http import urlencode
from rest_framework import serializers
from vjit_network.core.models import File
from urllib.parse import urlparse
from typing import List
import extraction
import requests
import random

User = get_user_model()

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

def random_range(from_num : int, to_num : int):
    return random.randint(from_num, to_num)

class NotificationBuilder:
    notification = None

    def __init__(self, title, content, title_html, content_html, recipients: List[User]):
        self.title = title
        self.content = content
        self.title_html = title_html
        self.content_html = content_html
        self.recipients = recipients

    @classmethod
    def push(cls, title, content, title_html=None, content_html=None, recipients=[]):
        instance = cls(
            title=title,
            content=content,
            title_html=title_html or title,
            content_html=content_html or content,
            recipients=recipients
        )
        instance.notification = instance._push_notification()

    def _push_notification(self):
        from vjit_network.api.models import Notification
        notification = Notification.objects.create(
            title_plantext=self.title,
            content_plantext=self.content,
            title_html=self.title_html,
            content_html=self.content_html
        )
        notification.recipients.set(self.recipients)
        notification.update_fields(is_publish=True)
        return notification