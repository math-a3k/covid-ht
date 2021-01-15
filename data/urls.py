#
from django.urls import path

from . import views

app_name = 'data'

urlpatterns = [
    path('input',
         views.input,
         name="input"
         ),
    path('csv',
         views.CSV().as_view(),
         name="csv"
         ),
    path('<str:uuid>/edit',
         views.edit,
         name="edit"
         ),
    path('<str:uuid>',
         views.detail,
         name="detail"
         ),
    path('',
         views.public_list,
         name="public-list"
         ),
]
