#
from django.urls import (include, path)

from rest_framework.schemas import get_schema_view

from data.v1 import views as data_views


urlpatterns = [
    path('auth/', include('rest_framework.urls')),
    #
    path('data/<str:uuid>',
         data_views.DataReadUpdate().as_view(),
         name='data-ru'),
    path('data',
         data_views.DataListCreate().as_view(),
         name='data-lc'),
    #
    path('openapi', get_schema_view(
        title="covid-ht",
        description="REST API for covid-ht",
        version="1.0.0"
    ), name='openapi-schema'),
]
