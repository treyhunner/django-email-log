from __future__ import unicode_literals

from django.db import models

from django.utils.translation import ugettext_lazy as _


class Email(models.Model):

    """Model to store outgoing email information"""

    from_email = models.TextField(_("from email"))
    recipients = models.TextField(_("recipients"))
    subject = models.TextField(_("subject"))
    body = models.TextField(_("body"))
    ok = models.BooleanField(_("ok"), default=False, db_index=True)
    date_sent = models.DateTimeField(_("date sent"), auto_now_add=True,
                                     db_index=True)

    def body_as_string(self):
        """ In the admin we display the body as utf-8 decoded text.  However
              if the field is constructed with a string, decode does not exist
              and the template fails.  Not sure why a field could be bytes OR
              a string.....  I thought Python3 was supposed to fix all of this
              with unicode """
        if hasattr('decode', self.body):
            return self.body.decode('utf-8')
        else:
            return self.body

    def __str__(self):
        return "{s.recipients}: {s.subject}".format(s=self)

    class Meta:
        verbose_name = _("email")
        verbose_name_plural = _("emails")
        ordering = ('-date_sent',)
