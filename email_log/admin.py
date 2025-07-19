import json

from django.contrib import admin
from django.template.defaultfilters import linebreaksbr
from django.utils.html import format_html
from django.utils.translation import gettext as _

from .models import Attachment, Email, Log


class LogInline(admin.StackedInline):
    model = Log
    readonly_fields = [
        "type",
        "timestamp",
        "esp",
        "event_id",
        "reject_reason",
        "mta_response",
        "tags",
        "user_agent",
        "click_url",
        "raw",
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "type",
                    "timestamp",
                    "tags",
                ),
            },
        ),
        (
            _("Details"),
            {
                "fields": (
                    "esp",
                    "event_id",
                    "mta_response",
                    "reject_reason",
                    "user_agent",
                    "click_url",
                    "raw",
                ),
                "classes": ["collapse"],
            },
        ),
    )
    extra = 0

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class AttachmentInline(admin.StackedInline):
    model = Attachment
    verbose_name = "Attachment"
    verbose_name_plural = "Attachments"
    can_delete = False
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "file",
                    "name",
                    "mimetype",
                )
            },
        ),
    )
    readonly_fields = (
        "file",
        "name",
        "mimetype",
    )
    extra = 0

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class EmailAdmin(admin.ModelAdmin):
    list_display = ["recipients", "from_email", "subject", "date_sent", "ok"]
    list_filter = ["date_sent", "ok"]
    readonly_fields = [
        "from_email",
        "recipients",
        "cc_recipients",
        "bcc_recipients",
        "reply_to",
        "headers",
        "subject",
        "body_formatted",
        "html_message",
        "html_message_preview",
        "date_sent",
        "ok",
    ]
    inlines = [
        AttachmentInline,
        LogInline,
    ]
    search_fields = [
        "subject",
        "body",
        "recipients",
        "cc_recipients",
        "bcc_recipients",
        "extra_headers",
    ]
    exclude = ["body", "html_message", "extra_headers"]
    fieldsets = [
        (
            None,
            {
                "fields": (
                    "from_email",
                    "recipients",
                    "cc_recipients",
                    "bcc_recipients",
                    "reply_to",
                    "headers",
                    "subject",
                    "body_formatted",
                    "html_message_preview",
                    "date_sent",
                    "ok",
                )
            },
        ),
        (
            "Plain HTML message",
            {
                "classes": ("collapse",),
                "fields": ("html_message",),
            },
        ),
    ]

    def has_delete_permission(self, request, *args, **kwargs):
        return request.user.is_superuser

    def has_add_permission(self, *args, **kwargs):
        return False

    def headers(self, obj) -> str:
        return format_html("<pre>{}</pre>", json.dumps(obj.extra_headers, indent=2))

    headers.short_description = "Extra headers"

    def html_message_preview(self, obj):
        if obj.html_message:
            return format_html(
                '<iframe style="border: 1px solid #e8e8e8; max-width: 800px; max-height: 600px" srcdoc="{}"></iframe>',  # noqa: ignore E501
                obj.html_message,
            )
        else:
            return "No HTML content"

    html_message_preview.short_description = "HTML message"

    def body_formatted(self, obj):
        return linebreaksbr(obj.body)

    body_formatted.short_description = "body"


admin.site.register(Email, EmailAdmin)
