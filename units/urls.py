#
from django.urls import (include, path)

from . import views

app_name = 'units'

urlpatterns_unit = [
    path('users',
         views.unit_users_list,
         name="users-list"
         ),
    path('users/new',
         views.unit_users_new,
         name="users-new"
         ),
    path('users/<int:pk>',
         views.unit_users_detail,
         name="users-detail"
         ),
    path('users/<int:pk>/edit',
         views.unit_users_edit,
         name="users-edit"
         ),
    path('users/<int:pk>/set-password',
         views.unit_users_set_password,
         name="users-set-password"
         ),
    path('edit',
         views.unit_edit,
         name="edit"
         ),
    path('data',
         views.unit_data,
         name="data"
         ),
    path('data/csv',
         views.CSV().as_view(),
         name="data-csv"
         ),
    path('',
         views.unit_dashboard,
         name="dashboard"
         ),
]

urlpatterns_units = [
    path('current/', include((urlpatterns_unit, "current"))),
    path('<int:pk>',
         views.detail,
         name="detail"
         ),
    path('',
         views.list,
         name="list"
         ),
]
