#
from django.urls import path

from rest_framework.schemas import get_schema_view

from base.v1 import views as base_views
from data.v1 import views as data_views


urlpatterns = [
    path('classify',
         base_views.Classify().as_view(),
         name='classify'),
    path('classify_dataset',
         base_views.ClassifyDataset().as_view(),
         name='classify-dataset'),
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
