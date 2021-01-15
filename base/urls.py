#
from django.urls import (include, path)

from . import views

app_name = 'base'

urlpatterns = [
    path('',
         views.home,
         name="home"
         ),
    path('about',
         views.about,
         name="about"
         ),
    path('accounts/',
         include('django.contrib.auth.urls')
         ),
]
