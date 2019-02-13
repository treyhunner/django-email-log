from django.contrib import admin
from .models import Email


class EmailAdmin(admin.ModelAdmin):
    list_display = ['recipients', 'from_email', 'subject', 'date_sent', 'ok']
    list_filter = ['date_sent', 'ok']
    readonly_fields = ['date_sent', ]
    search_fields = ['subject', 'body', 'recipients']

    def has_delete_permission(self, *args, **kwargs):
        return False

    def has_add_permission(self, *args, **kwargs):
        return False


admin.site.register(Email, EmailAdmin)
