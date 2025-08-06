from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend
from email.mime.base import MIMEBase

import logging
from .conf import settings
from .models import Attachment, Email


class EmailBackend(BaseEmailBackend):
    """Wrapper email backend that records all emails in a database model"""

    def __init__(self, **kwargs):
        super(EmailBackend, self).__init__(**kwargs)
        self.connection = get_connection(settings.EMAIL_LOG_BACKEND, **kwargs)

    def send_messages(self, email_messages):
        num_sent = 0
        for message in email_messages:
            recipients = "; ".join(message.to)
            cc_recipients = "; ".join(message.cc) if message.cc else ""
            bcc_recipients = "; ".join(message.bcc) if message.bcc else ""
            email = None
            html_message = self._get_html_message(message)
            try:
                email = Email.objects.create(
                    from_email=message.from_email,
                    recipients=recipients,
                    cc_recipients=cc_recipients,
                    bcc_recipients=bcc_recipients,
                    subject=message.subject,
                    body=message.body,
                    html_message=html_message,
                )
            except Exception:
                logging.error(
                    "Failed to save email to database (create)", exc_info=True
                )

            if settings.EMAIL_LOG_SAVE_ATTACHMENTS:
                self._log_attachments(email, message)

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

    def _get_html_message(self, message: EmailMessage) -> str:
        """Retrieve html message from the email message."""
        if hasattr(message, "alternatives") and len(message.alternatives) > 0:
            for alternative in message.alternatives:
                if alternative[1] == "text/html":
                    return alternative[0]
        return ""

    def _log_attachments(self, email: Email, message: EmailMessage):
        """Retrieve all attachments from email and create them."""
        attachment_files = {}
        for attachment in message.attachments:
            if isinstance(attachment, MIMEBase):
                attachment_files[attachment.get_filename()] = {
                    "file": ContentFile(attachment.get_payload()),
                }
            else:
                name, content, type = attachment
                attachment_files[name] = {
                    "file": ContentFile(content),
                }
                if type != "application/octet-stream":
                    attachment_files[name].update({"mimetype": type})

        if attachment_files:
            self._create_attachments(email, attachment_files)

    def _create_attachments(self, email: Email, files: dict):
        """Create attachments and save it to database."""
        for filename, filedata in files.items():
            content = filedata.get("file", None)
            mimetype = filedata.get("mimetype", None)
            attachment = Attachment()

            attachment.name = filename
            attachment.email = email
            if mimetype:
                attachment.mimetype = mimetype

            attachment.file.save(
                filename,
                content=content,
                save=True,
            )
