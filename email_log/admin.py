from django.contrib import admin
from django.template.defaultfilters import linebreaksbr
from .models import Email


class EmailAdmin(admin.ModelAdmin):
    list_display = ['recipients', 'from_email', 'subject', 'date_sent', 'ok']
    list_filter = ['date_sent', 'ok']
    readonly_fields = ['from_email', 'recipients', 'subject', 'body_formatted',
                       'date_sent', 'ok']
    search_fields = ['subject', 'body', 'recipients']
    exclude = ['body']

    def has_delete_permission(self, *args, **kwargs):
        return False

    def has_add_permission(self, *args, **kwargs):
        return False
        
    def body_formatted(self, obj):
        return linebreaksbr(obj.body)
    body_formatted.short_description = "body"


admin.site.register(Email, EmailAdmin)
