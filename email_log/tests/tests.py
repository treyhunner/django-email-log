from __future__ import unicode_literals

from django.test import TestCase
from django.test.utils import override_settings
from django.utils.six import text_type
from django.core.mail import send_mail
from django.core import mail

from email_log.models import Email
from email_log.conf import Settings


class EmailModelTests(TestCase):

    def test_unicode(self):
        email = Email.objects.create(
            from_email="from@example.com",
            recipients="to@example.com",
            subject="Subject line",
            body="Message body",
            ok=True,
        )
        self.assertEqual(text_type(email), "to@example.com: Subject line")


class SettingsTests(TestCase):

    @override_settings(SPECIFIED_SETTING="specified")
    def test_settings_fall_through(self):
        settings = Settings()
        settings.defaults.UNSPECIFIED_SETTING = "unspecified"
        self.assertEqual(settings.SPECIFIED_SETTING, "specified")

    def test_settings_defaults(self):
        settings = Settings()
        settings.defaults.UNSPECIFIED_SETTING = "unspecified"
        self.assertEqual(settings.UNSPECIFIED_SETTING, "unspecified")


@override_settings(EMAIL_BACKEND='email_log.backends.EmailBackend')
class EmailBackendTests(TestCase):

    plain_args = {
        'from_email': "from@example.com",
        'recipients': ["to@example.com"],
        'subject': "Subject line",
        'body': "Message body",
    }

    def assertEmailCorrect(self, email, model=True, **kwargs):
        for key, value in kwargs.items():
            if key == 'recipients' and model:
                value = '; '.join(value)
            self.assertEqual(getattr(email, key), value)

    def send_mail(self, **kwargs):
        kwgs = dict(**kwargs)
        args = [kwgs.pop(k) for k in
                ('subject', 'body', 'from_email', 'recipients')]
        return send_mail(*args, **kwgs)

    def test_send_messages(self):
        sent = self.send_mail(fail_silently=False, **self.plain_args)
        self.assertEqual(sent, 1)
        self.assertEqual(len(mail.outbox), 1)
        email = Email.objects.get()
        self.assertTrue(email.ok)
        self.assertEqual(email.recipients, "to@example.com")
        self.assertSequenceEqual(mail.outbox[0].to, ["to@example.com"])
        for message in (email, mail.outbox[0]):
            self.assertEqual(message.from_email, "from@example.com")
            self.assertEqual(message.subject, "Subject line")
            self.assertEqual(message.body, "Message body")

    @override_settings(EMAIL_LOG_BACKEND='email_log.tests.backends.FailingEmailBackend')
    def test_send_failure(self):
        self.assertRaises(NotImplementedError, self.send_mail,
                          fail_silently=False, **self.plain_args)
        email = Email.objects.get()
        self.assertFalse(email.ok)
        self.assertEmailCorrect(email, **self.plain_args)

    @override_settings(EMAIL_LOG_BACKEND='email_log.tests.backends.FailingEmailBackend')
    def test_send_failure_silent(self):
        sent = self.send_mail(fail_silently=True, **self.plain_args)
        self.assertEqual(sent, 0)
        email = Email.objects.get()
        self.assertFalse(email.ok)
        self.assertEmailCorrect(email, **self.plain_args)
