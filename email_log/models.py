from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Email(models.Model):

    """Model to store outgoing email information"""

    from_email = models.TextField()
    recipients = models.TextField()
    subject = models.TextField()
    body = models.TextField()
    ok = models.BooleanField(default=False, db_index=True)
    date_sent = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return "{s.recipients}: {s.subject}".format(s=self)

    class Meta:
        ordering = ('-date_sent',)
