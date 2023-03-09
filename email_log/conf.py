from django.conf import settings as defined_settings


class Settings:

    """Class used for allowing default settings for app"""

    class Default:
        EMAIL_LOG_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
        EMAIL_LOG_SAVE_ATTACHMENTS = False
        EMAIL_LOG_ATTACHMENTS_PATH = ""

    def __init__(self):
        self.defaults = Settings.Default()

    def __getattr__(self, name):
        try:
            return getattr(defined_settings, name)
        except AttributeError:
            return getattr(self.defaults, name)


settings = Settings()
