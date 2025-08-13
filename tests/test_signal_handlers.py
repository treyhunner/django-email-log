from unittest.mock import Mock

from django.core.mail import EmailMultiAlternatives
from django.test import TestCase, modify_settings, override_settings
from django.utils.timezone import now

from anymail.signals import AnymailTrackingEvent, post_send, tracking

import email_log
from email_log.apps import EmailLogConfig
from email_log.models import Attachment, Email, Log
from email_log.signal_handlers import handle_tracking_event, log_successful_email


class EmailLogConfigTestCase(TestCase):
    @modify_settings(INSTALLED_APPS={"remove": "anymail"})
    @override_settings(EMAIL_LOG_CONNECT_ANYMAIL_SIGNALS=False)
    def test_anymail_not_installed_signals_disabled(self):
        app_config = EmailLogConfig("email_log_tests", email_log)
        app_config.ready()
        self.assertNotIn(handle_tracking_event, [r[1]() for r in tracking.receivers])
        self.assertNotIn(log_successful_email, [r[1]() for r in post_send.receivers])

    @modify_settings(INSTALLED_APPS={"remove": "anymail"})
    @override_settings(EMAIL_LOG_CONNECT_ANYMAIL_SIGNALS=True)
    def test_anymail_not_installed_signals_enabled(self):
        app_config = EmailLogConfig("email_log_tests", email_log)
        app_config.ready()
        self.assertNotIn(handle_tracking_event, [r[1]() for r in tracking.receivers])
        self.assertNotIn(log_successful_email, [r[1]() for r in post_send.receivers])

    @modify_settings(INSTALLED_APPS={"append": "anymail"})
    @override_settings(EMAIL_LOG_CONNECT_ANYMAIL_SIGNALS=False)
    def test_anymail_installed_signals_disabled(self):
        app_config = EmailLogConfig("email_log_tests", email_log)
        app_config.ready()
        self.assertNotIn(handle_tracking_event, [r[1]() for r in tracking.receivers])
        self.assertNotIn(log_successful_email, [r[1]() for r in post_send.receivers])

    @modify_settings(INSTALLED_APPS={"append": "anymail"})
    @override_settings(EMAIL_LOG_CONNECT_ANYMAIL_SIGNALS=True)
    def test_signals_installed_signals_enabled(self):
        app_config = EmailLogConfig("email_log_tests", email_log)
        app_config.ready()
        self.assertIn(handle_tracking_event, [r[1]() for r in tracking.receivers])
        self.assertIn(log_successful_email, [r[1]() for r in post_send.receivers])


class LogSuccessfulEmailTestCase(TestCase):
    def setUp(self):
        self.text_content = "Test email text content"
        self.html_content = "<p>Test email HTML content</p>"
        self.message = EmailMultiAlternatives(
            "Subject here",
            self.text_content,
            "from@example.com",
            ["to@example.com"],
            headers={"List-Unsubscribe": "<mailto:unsub@example.com>"},
        )
        self.message.attach_alternative(self.html_content, "text/html")

    # Delete any attachment files so we don't leave them on-disk
    def tearDown(self):
        for attachment in Attachment.objects.all():
            attachment.file.delete(save=False)
            attachment.delete()

    def test_log_successful_email(self):
        mock_status = Mock()
        mock_status.message_id = "4561230987"

        self.assertQuerySetEqual(Email.objects.all(), Email.objects.none())

        log_successful_email(
            sender=Mock(),
            message=self.message,
            status=mock_status,
            esp_name="test_esp",
        )

        self.assertEqual(Email.objects.count(), 1)
        email = Email.objects.first()
        self.assertEqual(email.html_message, self.html_content)

    @override_settings(EMAIL_LOG_SAVE_ATTACHMENTS=False)
    def test_log_successful_email_but_no_attachments(self):
        self.assertQuerySetEqual(Attachment.objects.all(), Attachment.objects.none())

        self.test_log_successful_email()

        self.assertQuerySetEqual(Attachment.objects.all(), Attachment.objects.none())

    @override_settings(EMAIL_LOG_SAVE_ATTACHMENTS=True)
    def test_log_successful_email_with_attachments(self):
        self.message.attach("data.json", '{"raw": "data"}', "application/json")
        cd_catalog_1 = """
            <catalog>
              <cd>
                <title>Bad Animals</title>
                <artist>Heart</artist>
              </cd>
              <cd>
                <title>Going To California</title>
                <artist>Led Zeppelin</artist>
              </cd>
            </catalog>
        """
        cd_catalog_2 = """
            <catalog>
              <cd>
                <title>Bohemian Rhapsody</title>
                <artist>Queen</artist>
              </cd>
            </catalog>
        """
        self.message.attach("cd_catalog_1.xml", cd_catalog_1, "application/xml")
        # Attachments with application/octet-stream mimetypes do not have their
        # mimetypes saved
        self.message.attach(
            "cd_catalog_2.ext", cd_catalog_2, "application/octet-stream"
        )

        self.assertQuerySetEqual(Attachment.objects.all(), Attachment.objects.none())

        self.test_log_successful_email()

        self.assertEqual(Attachment.objects.count(), 3)
        self.assertEqual(
            list(
                Attachment.objects.all()
                .order_by("mimetype")
                .values_list("mimetype", flat=True)
            ),
            [
                "",
                "application/json",
                "application/xml",
            ],
        )


class HandleTrackingEventTestCase(TestCase):
    def setUp(self):
        self.event = AnymailTrackingEvent(
            event_type="custom_event",
            message_id="4321",
            event_id="1234567890",
            timestamp=now(),
            esp_event="Custom ESP event data",
        )

    def test_handle_tracking_event_without_email(self):
        email = Email.objects.create()

        # Without an email to correlate, we do nothing
        self.assertEqual(
            handle_tracking_event(
                sender=Mock(),
                event=self.event,
                esp_name="test_esp",
            ),
            None,
        )
        self.assertQuerySetEqual(email.logs.all(), Log.objects.none())

    def test_handle_tracking_event_with_email(self):
        email = Email.objects.create(
            extra_headers={
                "anymail_id": "4321",
            },
        )

        self.assertEqual(email.logs.count(), 0)

        # Without an email to correlate, we do nothing
        handle_tracking_event(
            sender=Mock(),
            event=self.event,
            esp_name="test_esp",
        )

        self.assertEqual(Log.objects.count(), 1)
        log: Log = Log.objects.first()
        self.assertEqual(log.email, email)
        self.assertEqual(log.esp, "test_esp")
        self.assertEqual(log.type, "custom_event")
        self.assertEqual(log.raw, "Custom ESP event data")
