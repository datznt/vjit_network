"""hutechsocial URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework.documentation import include_docs_urls
from django.conf import settings
from django.contrib.staticfiles.urls import static
# from rest_framework_cache.registry import cache_registry

urlpatterns = [
    # backend
    url('', admin.site.urls),
    url('', include('vjit_network.core.urls')),
    url('grappelli/', include('grappelli.urls')),
    url('api/', include('vjit_network.api.urls', namespace='vjit_network.api')),
    url('api/docs/', include_docs_urls(title='Alumni career')),
    # frontend
    
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# You must execute autodiscover to load your serializers. To do this change your urls.py adding the following code (sunch as Django admin):
# cache_registry.autodiscover()