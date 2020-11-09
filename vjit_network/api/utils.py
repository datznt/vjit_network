from urllib.parse import urlparse
from vjit_network.core.models import File
from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.urls import reverse as base_reverse
from django.contrib.sites.models import Site
from django.utils.http import urlencode
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


def reverse(view, urlconf=None, args=None, kwargs=None, current_app=None, query_kwargs=None):
    '''Custom reverse to handle query strings.
    Usage:
        reverse('app.views.my_view', kwargs={'pk': 123}, query_kwargs={'search', 'Bob'})
    '''
    base_url = base_reverse(view, urlconf=urlconf, args=args,
                            kwargs=kwargs, current_app=current_app)
    # default_site_settings = Site.objects.get_current()
    # base_url = default_site_settings.domain + base_url
    if query_kwargs:
        return '{}?{}'.format(base_url, urlencode(query_kwargs))
    return base_url


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