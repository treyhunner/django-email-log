import pathlib

from django.db import models
from django.utils.translation import gettext_lazy as _

from .conf import settings


class Email(models.Model):

    """Model to store outgoing email information"""

    from_email = models.TextField(_("from email"))
    recipients = models.TextField(_("recipients"))
    subject = models.TextField(_("subject"))
    body = models.TextField(_("body"))
    ok = models.BooleanField(_("ok"), default=False, db_index=True)
    date_sent = models.DateTimeField(_("date sent"), auto_now_add=True, db_index=True)
    html_message = models.TextField(_("HTML message"), blank=True)
    err_msg = models.TextField(_("Error message"), blank=True)

    def __str__(self):
        return "{s.recipients}: {s.subject}".format(s=self)

    class Meta:
        verbose_name = _("email")
        verbose_name_plural = _("emails")
        ordering = ("-date_sent",)


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
