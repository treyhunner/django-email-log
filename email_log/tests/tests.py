from contextlib import contextmanager

from django.apps import apps
from django.core import checks
from django.db.models.signals import post_save
from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core import mail

from email_log.models import Email
from email_log.conf import Settings

FAILING_BACKEND = "email_log.tests.backends.FailingEmailBackend"


@contextmanager
def connect_signal(signal, receiver, *args, **kwargs):
    signal.connect(receiver, *args, **kwargs)
    try:
        yield
    finally:
        assert signal.disconnect(receiver, *args, **kwargs)


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


@override_settings(EMAIL_BACKEND="email_log.backends.EmailBackend")
class EmailBackendTests(TestCase):

    plain_args = {
        "from_email": "from@example.com",
        "recipients": ["to@example.com"],
        "subject": "Subject line",
        "body": "Message body",
    }

    def assertEmailCorrect(self, email, model=True, **kwargs):
        for key, value in kwargs.items():
            if key == "recipients" and model:
                value = "; ".join(value)
            self.assertEqual(getattr(email, key), value)

    def send_mail(self, **kwargs):
        kwgs = dict(**kwargs)
        args = [kwgs.pop(k) for k in ("subject", "body", "from_email", "recipients")]
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
        self.assertRaises(
            NotImplementedError, self.send_mail, fail_silently=False, **self.plain_args
        )
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

    def test_send_db_problem_create(self):
        def break_created(sender, instance, created, **kwargs):
            if created:
                raise Exception("DB problem")

        with connect_signal(post_save, break_created, sender=Email):
            with self.assertLogs() as captured:
                sent = self.send_mail(fail_silently=True, **self.plain_args)
                self.assertEqual(sent, 1)
                self.assertEqual(len(captured.records), 1)
                self.assertEqual(
                    captured.records[0].getMessage(),
                    "Failed to save email to database (create)",
                )

    def test_send_db_problem_update(self):
        def break_update(sender, instance, created, **kwargs):
            if not created:
                raise Exception("DB problem")

        with connect_signal(post_save, break_update, sender=Email):
            with self.assertLogs() as captured:
                sent = self.send_mail(fail_silently=True, **self.plain_args)
                self.assertEqual(sent, 1)
                self.assertEqual(len(captured.records), 1)
                self.assertEqual(
                    captured.records[0].getMessage(),
                    "Failed to save email to database (update)",
                )


class AdminTests(TestCase):
    def setUp(self):
        user = User(username="user", is_superuser=True, is_staff=True)
        user.set_password("pass")
        user.save()
        self.client.login(username="user", password="pass")

    def test_add_page(self):
        page = self.client.get("/admin/email_log/email/add/")
        self.assertEqual(page.status_code, 403)

    def test_body_is_formatted(self):
        initial = "This\nis\na\ntest"
        email = Email.objects.create(body=initial)
        page = self.client.get(
            "/admin/email_log/email/{}/".format(email.pk),
            follow=True,
        )
        self.assertNotContains(
            page,
            '<div class="form-row field-body">',
            html=True,
        )
        self.assertNotContains(page, initial, html=True)
        self.assertContains(
            page,
            '<div class="form-row field-body_formatted">',
            html=False,  # html=False needed for partial HTML match
        )
        self.assertContains(page, "This<br>is<br>a<br>test", html=True)
        self.assertEqual(page.status_code, 200)

    def test_delete_page(self):
        email = Email.objects.create()
        page = self.client.get("/admin/email_log/email/{0}/delete/".format(email.pk))
        self.assertEqual(page.status_code, 403)

    def test_app_name(self):
        page = self.client.get("/admin/")
        self.assertContains(page, "Email log")


class ChecksTest(TestCase):
    def test_not_raising_warning_check(self):
        warnings = checks.run_checks(app_configs=apps.get_app_configs())
        self.assertEqual(len(warnings), 0)
