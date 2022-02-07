from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend
import logging
from .conf import settings
from .models import Email


class EmailBackend(BaseEmailBackend):

    """Wrapper email backend that records all emails in a database model"""

    def __init__(self, **kwargs):
        super(EmailBackend, self).__init__(**kwargs)
        self.connection = get_connection(settings.EMAIL_LOG_BACKEND, **kwargs)

    def send_messages(self, email_messages):
        num_sent = 0
        for message in email_messages:
            recipients = "; ".join(message.to)
            email = None
            try:
                email = Email.objects.create(
                    from_email=message.from_email,
                    recipients=recipients,
                    subject=message.subject,
                    body=message.body,
                )
            except Exception:
                logging.error(
                    "Failed to save email to database (create)", exc_info=True
                )
            message.connection = self.connection
            num_sent += message.send()
            if num_sent > 0 and email:
                email.ok = True
                try:
                    email.save()
                except Exception:
                    logging.error(
                        "Failed to save email to database (update)", exc_info=True
                    )
        return num_sent
