from django.contrib import admin
from .models import *


class MmAlertAdmin(admin.ModelAdmin):
    fields = ['stock', 'timeframe', 'smm', 'emm', 'active']

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

admin.site.register(MmAlert, MmAlertAdmin)
