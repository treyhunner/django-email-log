from django.apps import AppConfig
from django.conf import settings as django_settings

from .conf import settings


class EmailLogConfig(AppConfig):
    name = "email_log"
    verbose_name = "Email log"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        if "anymail" in django_settings.INSTALLED_APPS:
            from anymail.signals import post_send, tracking
            from .signal_handlers import handle_tracking_event, log_successful_email

            if settings.EMAIL_LOG_CONNECT_ANYMAIL_SIGNALS:
                tracking.connect(handle_tracking_event)
                post_send.connect(log_successful_email)
