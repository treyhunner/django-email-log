from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend
from email.mime.base import MIMEBase

import logging
from .conf import settings
from .models import Attachment, Email

ERR_TEMPLATE = "An exception of type {0} occurred. Arguments:\n{1!r}"

class EmailBackend(BaseEmailBackend):

    """Wrapper email backend that records all emails in a database model"""

    def __init__(self, **kwargs):
        super(EmailBackend, self).__init__(**kwargs)
        self.connection = get_connection(settings.EMAIL_LOG_BACKEND, **kwargs)
        self.LOGGED_SUBJECTS = settings.EMAIL_LOG_SUBJECTS

    def send_messages(self, email_messages, log_on_db=False):
        for message in email_messages:
            recipients = "; ".join(message.to)
            email = None
            html_message = self._get_html_message(message)
            
            # Log only if subject defined in the settings match
            if not self.LOGGED_SUBJECTS:
                # if not define log everything
                log_on_db = True
            else:
                log_on_db = any(
                    subject.lower() in message.subject.lower() for subject in self.LOGGED_SUBJECTS
                )

            if log_on_db: 
                logging.info("Message subject matched, Saving mail log")
                try:
                    email = Email.objects.create(
                        from_email=message.from_email,
                        recipients=recipients,
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
            
            try:
                message.send(fail_silently=False)
                status = True
                err_msg = ""
            except Exception as e:
                logging.error(f"Error while sending mail: {e}")
                status = False
                err_msg = ERR_TEMPLATE.format(type(e).__name__, e.args)

            if email:
                email.ok = status
                email.err_msg = err_msg
                try:
                    email.save()
                except Exception:
                    logging.error(
                        "Failed to save email to database (update)", exc_info=True
                    )

        return status

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
