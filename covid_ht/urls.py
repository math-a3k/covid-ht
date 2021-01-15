"""covid_ht URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import (include, path)
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.i18n import JavaScriptCatalog

from base.urls import urlpatterns as base_urls
from data.urls import urlpatterns as data_urls
from units.urls import urlpatterns_unit as unit_urls
from units.urls import urlpatterns_units as units_urls


def get_version():
    return timezone.now().timestamp()


urlpatterns = [
    path(
        'jsi18n/',
        cache_page(86400, key_prefix='js18n-%s' % get_version())(
            JavaScriptCatalog.as_view()
        ),
        name='javascript-catalog'
    ),
    path('nested_admin/',
         include('nested_admin.urls')),
    path('admin/', admin.site.urls),
    path('django-ai/',
         include('django_ai.ai_base.urls')),
    #
    path('data/', include((data_urls, "data"))),
    path('units/', include((units_urls, "units"))),
    # path('unit/', include((unit_urls, "unit"))),
    path('', include((base_urls, "base"))),
]
