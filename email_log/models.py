from django.db import models
from django.utils.translation import gettext_lazy as _


class Email(models.Model):

    """Model to store outgoing email information"""

    from_email = models.TextField(_("from email"))
    recipients = models.TextField(_("recipients"))
    subject = models.TextField(_("subject"))
    body = models.TextField(_("body"))
    ok = models.BooleanField(_("ok"), default=False, db_index=True)
    date_sent = models.DateTimeField(_("date sent"), auto_now_add=True, db_index=True)

    def __str__(self):
        return "{s.recipients}: {s.subject}".format(s=self)

    class Meta:
        verbose_name = _("email")
        verbose_name_plural = _("emails")
        ordering = ("-date_sent",)
