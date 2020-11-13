from django.urls import reverse as base_reverse
from django.utils.http import urlencode
from django.template.defaultfilters import truncatechars

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

def truncate_string(string):
    if not string:
        return None
    return truncatechars(string,100)