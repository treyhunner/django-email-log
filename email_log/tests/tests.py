from contextlib import contextmanager

from django.apps import apps
from django.core import checks
from django.db.models.signals import post_save
from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mail
from django.core import mail
from email.mime.text import MIMEText

from email_log.models import Attachment, Email
from email_log.conf import Settings

import shutil
import os

FAILING_BACKEND = "email_log.tests.backends.FailingEmailBackend"
ATTACHMENTS_TEST_FOLDER = "testfiles"


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


class AttachmentModelTests(TestCase):
    def setUp(self):
        self.email = Email.objects.create(
            from_email="from@example.com",
            recipients="to@example.com",
            subject="Subject line",
            body="Message body",
            ok=True,
        )

    def test_unicode(self):
        file_name = "Test name"
        file_content = b"Test content"
        test_file = ContentFile(file_content)

        attachment = Attachment(
            name=file_name,
            file=test_file,
            mimetype="text/plain",
            email=self.email,
        )
        self.assertEqual(str(attachment), file_name)


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
    @classmethod
    def setUpClass(cls):
        # Create test folder
        os.mkdir(ATTACHMENTS_TEST_FOLDER)
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        # Remove test folder
        shutil.rmtree(ATTACHMENTS_TEST_FOLDER)
        return super().tearDownClass()

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

    def get_number_of_test_files(self):
        return len(
            [
                entry
                for entry in os.listdir(ATTACHMENTS_TEST_FOLDER)
                if os.path.isfile(os.path.join(ATTACHMENTS_TEST_FOLDER, entry))
            ]
        )

    def send_mail(self, **kwargs):
        kwgs = dict(**kwargs)
        args = [kwgs.pop(k) for k in ("subject", "body", "from_email", "recipients")]
        return send_mail(*args, **kwgs)

    def send_mail_with_attachment(self, attachment_data):
        args = {
            **self.plain_args,
            "to": self.plain_args["recipients"],
        }
        args.pop("recipients")
        message = EmailMessage(**args)
        message.attach(**attachment_data)
        return message.send()

    def test_send_messages(self):
        sent = self.send_mail(fail_silently=False, **self.plain_args)
        self.assertEmailOK(sent)

    @override_settings(EMAIL_LOG_SAVE_ATTACHMENTS=True)
    def test_send_messages_without_attachment_when_setting_is_set(self):
        sent = self.send_mail(fail_silently=False, **self.plain_args)
        self.assertEmailOK(sent)

    def test_send_messages_with_attachment_when_setting_is_not_set(self):
        attachment_data = {
            "filename": f"{ATTACHMENTS_TEST_FOLDER}/test.txt",
            "content": b"test",
            "mimetype": "text/plain",
        }
        attachments_number = self.get_number_of_test_files()
        sent = self.send_mail_with_attachment(attachment_data)

        self.assertEmailOK(sent)
        self.assertEqual(Attachment.objects.count(), 0)
        self.assertEqual(self.get_number_of_test_files(), attachments_number)

    @override_settings(EMAIL_LOG_SAVE_ATTACHMENTS=True)
    def test_send_messages_with_attachment(self):
        attachment_data = {
            "filename": f"{ATTACHMENTS_TEST_FOLDER}/test.txt",
            "content": b"test",
            "mimetype": "text/plain",
        }
        self.assertAttachmentOK(attachment_data, expected_data=attachment_data)

    @override_settings(EMAIL_LOG_ATTACHMENTS_PATH=ATTACHMENTS_TEST_FOLDER)
    @override_settings(EMAIL_LOG_SAVE_ATTACHMENTS=True)
    def test_send_messages_with_attachment_with_path_specified(self):
        attachment_data = {
            "filename": "test.txt",
            "content": b"test",
            "mimetype": "text/plain",
        }
        self.assertAttachmentOK(attachment_data, expected_data=attachment_data)

    @override_settings(EMAIL_LOG_SAVE_ATTACHMENTS=True)
    def test_send_messages_with_mime_base_attachment(self):
        mime_base_message = MIMEText("Test message")
        mime_base_message.add_header(
            "Content-ID",
            f"{ATTACHMENTS_TEST_FOLDER}/<{{test.txt}}>",
        )
        mime_base_message.add_header(
            "Content-Disposition",
            "inline",
            filename=f"{ATTACHMENTS_TEST_FOLDER}/test.txt",
        )
        attachment_data = {
            "filename": mime_base_message,
        }
        expected_data = {
            "filename": f"{ATTACHMENTS_TEST_FOLDER}/test.txt",
            "content": b"Test message",
        }
        self.assertAttachmentOK(attachment_data, expected_data)

    @override_settings(EMAIL_LOG_SAVE_ATTACHMENTS=True)
    def test_send_messages_with_attachment_without_type(self):
        attachment_data = {
            "filename": f"{ATTACHMENTS_TEST_FOLDER}/test",
            "content": b"test",
        }
        self.assertAttachmentOK(attachment_data, expected_data=attachment_data)

    def test_send_html_message(self):
        html_message = "<strong>Test html</strong><br>"
        args = {
            **self.plain_args,
            "to": self.plain_args["recipients"],
        }
        args.pop("recipients")

        message = EmailMultiAlternatives(**args)
        message.attach_alternative(html_message, "text/html")

        sent = message.send()
        self.assertEqual(sent, 1)
        self.assertEqual(len(mail.outbox), 1)

        email = Email.objects.get()
        self.assertEqual(email.html_message, html_message)

    def test_send_message_with_not_html_alternative(self):
        text_message = "test"
        args = {
            **self.plain_args,
            "to": self.plain_args["recipients"],
        }
        args.pop("recipients")

        message = EmailMultiAlternatives(**args)
        message.attach_alternative(text_message, "text/plain")

        sent = message.send()
        self.assertEqual(sent, 1)
        self.assertEqual(len(mail.outbox), 1)

        email = Email.objects.get()
        self.assertEqual(email.html_message, "")

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

    def assertEmailOK(self, sent):
        self.assertEqual(sent, 1)
        self.assertEqual(len(mail.outbox), 1)
        email = Email.objects.get()
        self.assertTrue(email.ok)
        self.assertEqual(email.recipients, self.plain_args["recipients"][0])
        self.assertSequenceEqual(mail.outbox[0].to, self.plain_args["recipients"])
        for message in (email, mail.outbox[0]):
            self.assertEqual(message.from_email, self.plain_args["from_email"])
            self.assertEqual(message.subject, self.plain_args["subject"])
            self.assertEqual(message.body, self.plain_args["body"])

    def assertAttachmentOK(self, attachment_data: dict, expected_data):
        number_of_attachments = self.get_number_of_test_files()
        sent = self.send_mail_with_attachment(attachment_data)

        self.assertEqual(sent, 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(self.get_number_of_test_files(), number_of_attachments + 1)

        email = Email.objects.get()
        saved_attachment = Attachment.objects.get()

        self.assertEqual(saved_attachment.name, expected_data.get("filename"))
        self.assertEqual(saved_attachment.file.read(), expected_data.get("content"))
        self.assertEqual(saved_attachment.email, email)

        type = expected_data.get("mimetype")
        if type is not None:
            self.assertEqual(saved_attachment.mimetype, type)


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
