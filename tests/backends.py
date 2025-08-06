from django.core.mail.backends.base import BaseEmailBackend


class FailingEmailBackend(BaseEmailBackend):
    """Email backend which always fails to send email"""

    def send_messages(self, email_messages):
        try:
            super(FailingEmailBackend, self).send_messages(email_messages)
        except NotImplementedError:
            if not self.fail_silently:
                raise
            return 0
