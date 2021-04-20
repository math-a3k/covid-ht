from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _

from django_ai.supervised_learning.admin import \
    HGBTreeClassifierAdmin, SVCAdmin

from .models import (
    CurrentClassifier, DecisionTree, ExternalClassifier, NetworkErrorLog,
    NetworkNode, SVM, User, )


class CovidHTUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = User


class CovidHTUserAdmin(UserAdmin):

    form = CovidHTUserChangeForm
    list_display = (
        'unit',
        'user_type', 'username', 'email', 'name',
        'is_active', 'date_joined', 'is_staff'
    )
    list_display_links = ('username', )
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

    fieldsets = (
        (_("Local Classifier"), {
            'fields': (
                ('classifier', 'external'),
            ),
        }),
        (_("Network Voting"), {
            'fields': (
                ('network_voting', ),
                ('breaking_ties_policy',),
                ('network_voting_threshold',),
            ),
        }),
    )

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context["nodes"] = NetworkNode.objects.all()
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )


@admin.register(ExternalClassifier)
class ExternalClassifierAdmin(admin.ModelAdmin):
    fieldsets = (
        (_("General"), {
            'fields': (
                ('name', ),
                ('remote_user', 'remote_user_token'),
            ),
        }),
        (_("URL and Endpoints"), {
            'fields': (
                ('service_url', 'timeout'),
                ('endpoint_classify', 'endpoint_classify_dataset'),
            ),
        }),
        (_("Metrics"), {
            'fields': (
                ('metrics',),
            ),
        }),
        (_("Other"), {
            'classes': ('collapse',),
            'fields': (
                ('metadata',),
            ),
        }),
    )
    readonly_fields = ['metadata', ]


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
                ('remote_user', 'remote_user_token'),
            ),
        }),
        (_("URL and Endpoints"), {
            'fields': (
                ('service_url', 'timeout'),
                ('endpoint_data',),
                ('endpoint_classify', 'endpoint_classify_dataset'),
            ),
        }),
        (_("Metrics"), {
            'fields': (
                ('metrics',),
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
                ('metadata',),
            ),
        }),
    )
    readonly_fields = ['metadata', ]


@admin.register(NetworkErrorLog)
class NetworkErrorLogAdmin(admin.ModelAdmin):
    pass
