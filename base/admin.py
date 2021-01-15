#
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
# from django.utils.translation import gettext_lazy as _

from .models import (CurrentClassifier, User)


class CovidHTUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = User


class CovidHTUserAdmin(UserAdmin):

    form = CovidHTUserChangeForm
    list_display = (
        'unit',
        'user_type', 'email', 'name',
        'is_active', 'date_joined', 'is_staff'
    )
    list_display_links = ('email', 'name')
    list_filter = (
        'unit',
        'user_type', ) + UserAdmin.list_filter
    fieldsets = (
        (None, {'fields': (
            'unit',
            'user_type',)}),
    ) + UserAdmin.fieldsets


admin.site.register(User, CovidHTUserAdmin)


@admin.register(CurrentClassifier)
class CurrentClassifierAdmin(admin.ModelAdmin):
    pass
