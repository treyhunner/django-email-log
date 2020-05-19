from unittest import skipUnless

from django import VERSION
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core import mail

from email_log.models import Email
from email_log.conf import Settings

FAILING_BACKEND = 'email_log.tests.backends.FailingEmailBackend'


class EmailModelTests(TestCase):

    def test_unicode(self):
        email = Email.objects.create(
            from_email="from@example.com",
            recipients="to@example.com",
            subject="Subject line",
            body="Message body",
            ok=True,
        )
        self.assertEqual(str(email), "to@example.com: Subject line")


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

    @override_settings(EMAIL_LOG_BACKEND=FAILING_BACKEND)
    def test_send_failure(self):
        self.assertRaises(NotImplementedError, self.send_mail,
                          fail_silently=False, **self.plain_args)
        email = Email.objects.get()
        self.assertFalse(email.ok)
        self.assertEmailCorrect(email, **self.plain_args)

    @override_settings(EMAIL_LOG_BACKEND=FAILING_BACKEND)
    def test_send_failure_silent(self):
        sent = self.send_mail(fail_silently=True, **self.plain_args)
        self.assertEqual(sent, 0)
        email = Email.objects.get()
        self.assertFalse(email.ok)
        self.assertEmailCorrect(email, **self.plain_args)


class AdminTests(TestCase):

    def setUp(self):
        user = User(username="user", is_superuser=True, is_staff=True)
        user.set_password("pass")
        user.save()
        self.client.login(username="user", password="pass")

    def test_add_page(self):
        page = self.client.get('/admin/email_log/email/add/')
        self.assertEqual(page.status_code, 403)

    def test_body_is_formatted(self):
        initial = "This\nis\na\ntest"
        email = Email.objects.create(body=initial)
        page = self.client.get('/admin/email_log/email/%s/' % email.pk, follow=True)
        self.assertNotIn(b'<div class="form-row field-body">', page.content)
        self.assertNotIn(initial.encode('utf-8'), page.content)
        self.assertIn(b'<div class="form-row field-body_formatted">',
                      page.content)
        self.assertContains(page, 'This<br>is<br>a<br>test', html=True)
        self.assertEqual(page.status_code, 200)

    def test_delete_page(self):
        email = Email.objects.create()
        page = self.client.get('/admin/email_log/email/{0}/delete/'
                               .format(email.pk))
        self.assertEqual(page.status_code, 403)

    def test_app_name(self):
        page = self.client.get('/admin/')
        if VERSION < (1, 7, 0):
            self.assertContains(page, "Email_Log")
        else:
            self.assertContains(page, "Email log")


class SouthSupportTests(TestCase):

    @skipUnless(VERSION < (1, 7, 0), "test only applies to 1.6 and below")
    def test_import_migrations_module(self):
        try:
            from email_log.migrations import __doc__  # noqa
        except ImproperlyConfigured as e:
            exception = e
        self.assertIn("SOUTH_MIGRATION_MODULES", exception.args[0])
