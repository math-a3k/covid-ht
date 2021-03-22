#
from django.contrib import admin

from .models import (Data, )


@admin.register(Data)
class DataAdmin(admin.ModelAdmin):
    readonly_fields = ('chtuid', 'uuid', )
