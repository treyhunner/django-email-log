from email.mime.base import MIMEBase
from typing import Any, Type

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.core.mail.backends.base import BaseEmailBackend
from django.db import transaction

from anymail.webhooks.base import AnymailCoreWebhookView
from anymail.message import AnymailStatus
from anymail.signals import AnymailTrackingEvent
from email_log.models import Email, Attachment, Log as EmailLog


def handle_tracking_event(
    sender: Type[AnymailCoreWebhookView],
    event: AnymailTrackingEvent,
    esp_name: str,
    **kwargs: Any,
) -> None:
    if (
        email := Email.objects.filter(extra_headers__anymail_id=event.message_id)
        .only("pk")
        .first()
    ):
        EmailLog.objects.create(
            email=email,
            type=event.event_type,
            esp=esp_name,
            metadata=event.metadata,
            timestamp=event.timestamp,
            event_id=event.event_id,
            reject_reason=event.reject_reason,
            mta_response=event.mta_response,
            tags=event.tags,
            user_agent=event.user_agent,
            click_url=event.click_url,
            raw=event.esp_event,
        )


def get_html_message(message: EmailMessage) -> str:
    if hasattr(message, "alternatives") and len(message.alternatives) > 0:
        for alternative in message.alternatives:
            if alternative[1] == "text/html":
                return alternative[0]
    return ""


def log_successful_email(
    sender: BaseEmailBackend,
    message: EmailMessage,
    status: AnymailStatus,
    esp_name: str,
    **kwargs: Any,
) -> None:
    message_headers = dict(message.message()._headers)
    for key in list(message_headers.keys()):
        if key.lower() in [
            "content-type",
            "date",
            "from",
            "mime-version",
            "subject",
            "to",
        ]:
            del message_headers[key]
    with transaction.atomic():
        email = Email.objects.create(
            recipients="; ".join(message.to),
            cc_recipients="; ".join(message.cc) if message.cc else "",
            bcc_recipients="; ".join(message.bcc) if message.bcc else "",
            reply_to="; ".join(message.reply_to) if message.reply_to else "",
            extra_headers=(
                message_headers
                | message.extra_headers  # noqa: ignore W503
                | {"anymail_id": status.message_id}  # noqa: ignore W503
            ),
            subject=message.subject,
            body=message.body,
            html_message=get_html_message(message),
            ok=True,
        )

        if getattr(settings, "EMAIL_LOG_SAVE_ATTACHMENTS", True):
            for attachment in message.attachments:
                mimetype = None
                if isinstance(attachment, MIMEBase):
                    name = attachment.get_filename()
                    content = ContentFile(attachment.get_payload())
                else:
                    name, content, attachment_type = attachment
                    content = ContentFile(content)
                    if attachment_type != "application/octet-stream":
                        mimetype = attachment_type

                db_attachment = Attachment.objects.create(
                    email=email,
                    name=name,
                    mimetype=mimetype,
                )
                db_attachment.file.save(
                    filename=name,
                    content=content,
                    save=True,
                )
