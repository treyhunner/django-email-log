import pathlib

from django.contrib.postgres.indexes import GinIndex
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _

from .conf import settings


class Email(models.Model):
    """Model to store outgoing email information"""

    from_email = models.TextField(_("from email"))
    recipients = models.TextField(_("recipients"))
    cc_recipients = models.TextField(_("cc recipients"), blank=True)
    bcc_recipients = models.TextField(_("bcc recipients"), blank=True)
    reply_to = models.TextField(_("reply to"), blank=True, default="")
    extra_headers = models.JSONField(encoder=DjangoJSONEncoder, default=dict)
    subject = models.TextField(_("subject"))
    body = models.TextField(_("body"))
    ok = models.BooleanField(_("ok"), default=False, db_index=True)
    date_sent = models.DateTimeField(_("date sent"), auto_now_add=True, db_index=True)
    html_message = models.TextField(_("HTML message"), blank=True)

    def __str__(self):
        return "{s.recipients}: {s.subject}".format(s=self)

    class Meta:
        verbose_name = _("email")
        verbose_name_plural = _("emails")
        ordering = ("-date_sent",)
        indexes = [
            GinIndex(fields=["extra_headers"]),
        ]


def get_attachment_path(instance, filename: str) -> str:
    """Return attachments path from settings

    If attachments path is callable then call it and return result. Otherwise
    return path concatenated with the filename.

    """
    path = settings.EMAIL_LOG_ATTACHMENTS_PATH
    if callable(path):
        return path(instance, filename)
    return str(pathlib.Path(str(path)) / filename)


class Attachment(models.Model):
    """Model to store attachments of outgoing email"""

    file = models.FileField(
        _("file"),
        upload_to=get_attachment_path,
    )
    name = models.CharField(_("name"), max_length=255, help_text=_("filename"))
    email = models.ForeignKey(
        Email,
        related_name="attachments",
        verbose_name=_("email"),
        on_delete=models.CASCADE,
    )
    mimetype = models.CharField(max_length=255, default="", blank=True)

    class Meta:
        verbose_name = _("attachment")
        verbose_name_plural = _("attachments")

    def __str__(self):
        return self.name


class Log(models.Model):
    email = models.ForeignKey(Email, verbose_name=_("email"), on_delete=models.CASCADE)
    esp = models.CharField(verbose_name=_("ESP"), max_length=255)
    metadata = models.JSONField()
    type = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    event_id = models.TextField()
    mta_response = models.TextField(verbose_name=_("MTA Response"), null=True)
    reject_reason = models.TextField(null=True)
    tags = models.JSONField()
    user_agent = models.TextField(null=True)
    click_url = models.URLField(verbose_name="Click URL", null=True, max_length=4192)
    raw = models.JSONField()

    class Meta:
        ordering = ["email", "timestamp"]

    def __str__(self):
        return self.type
