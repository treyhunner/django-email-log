from typing import TYPE_CHECKING, Any, Type

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail.backends.base import BaseEmailBackend
from django.db import transaction

from email_log.backends import EmailBackend as EmailLogBackend
from email_log.models import Email, Log as EmailLog

if TYPE_CHECKING:  # pragma: no cover
    from anymail.webhooks.base import AnymailCoreWebhookView
    from anymail.message import AnymailStatus
    from anymail.signals import AnymailTrackingEvent


def handle_tracking_event(
    sender: "Type[AnymailCoreWebhookView]",
    event: "AnymailTrackingEvent",
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


def log_successful_email(
    sender: "BaseEmailBackend",
    message: "EmailMessage",
    status: "AnymailStatus",
    esp_name: str,
    **kwargs: Any,
) -> None:
    backend = EmailLogBackend()
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
            html_message=backend._get_html_message(message),
            ok=True,
        )

        if getattr(settings, "EMAIL_LOG_SAVE_ATTACHMENTS", True):
            backend._log_attachments(email=email, message=message)
