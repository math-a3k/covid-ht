from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _

from django_ai.supervised_learning.admin import \
    HGBTreeClassifierAdmin, SVCAdmin

from .models import (
    CurrentClassifier, DecisionTree, ExternalClassifier, NetworkNode,
    SVM, User, )


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


@admin.register(ExternalClassifier)
class ExternalClassifierAdmin(admin.ModelAdmin):
    pass


@admin.register(DecisionTree)
class DecisionTreeAdmin(HGBTreeClassifierAdmin):
    pass


@admin.register(SVM)
class SVMAdmin(SVCAdmin):
    pass


@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    fieldsets = (
        (_("General"), {
            'fields': (
                ('name', ),
                ('unit', 'user',),
            ),
        }),
        (_("URL and Endpoints"), {
            'fields': (
                ('node_url', ),
                ('endpoint_data',),
                ('endpoint_classify', 'endpoint_classify_set'),
            ),
        }),
        (_("Data Sharing"), {
            'fields': (
                ('data_sharing_is_enabled',),
                ('data_sharing_mode',),
            ),
        }),
        (_("Classification Service"), {
            'fields': (
                ('classification_request', ),
            ),
        }),
        (_("Other"), {
            'classes': ('collapse',),
            'fields': (
                ('last_updated', 'metadata',),
            ),
        }),
    )
