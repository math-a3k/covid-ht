#
from django.urls import (include, path)

from . import views

app_name = 'base'

urlpatterns = [
    path('',
         views.home,
         name="home"
         ),
    path('update-metadata/<int:pk>',
         views.UpdateMetadataView.as_view(),
         name="update_metadata"
         ),
    path('accounts/',
         include('django.contrib.auth.urls')
         ),
]
