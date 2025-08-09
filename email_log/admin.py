from django.contrib import admin
from django.template.defaultfilters import linebreaksbr
from django.utils.html import format_html
from .models import Attachment, Email


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


class EmailAdmin(admin.ModelAdmin):
    list_display = ["recipients", "from_email", "subject", "date_sent", "ok"]
    list_filter = ["date_sent", "ok"]
    readonly_fields = [
        "from_email",
        "recipients",
        "cc_recipients",
        "bcc_recipients",
        "reply_to",
        "extra_headers",
        "subject",
        "body_formatted",
        "html_message",
        "html_message_preview",
        "date_sent",
        "ok",
    ]
    inlines = [
        AttachmentInline,
    ]
    search_fields = [
        "subject",
        "body",
        "recipients",
        "cc_recipients",
        "bcc_recipients",
        "extra_headers",
    ]
    exclude = ["body", "html_message"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "from_email",
                    "recipients",
                    "cc_recipients",
                    "bcc_recipients",
                    "reply_to",
                    "extra_headers",
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
    )

    def has_delete_permission(self, *args, **kwargs):
        return False

    def has_add_permission(self, *args, **kwargs):
        return False

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
