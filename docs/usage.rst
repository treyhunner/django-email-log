Usage
=====

Installation
------------

Install from `PyPI`_:

.. code-block:: bash

    $ pip install django-email-log

.. _PyPI: https://pypi.python.org/pypi/django-email-log/


Quickstart
----------

Add ``email_log`` to ``INSTALLED_APPS`` in your settings file:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'email_log',
    )

Then set django-email-log as your email backend in your settings file:

.. code-block:: python

    EMAIL_BACKEND = 'email_log.backends.EmailBackend'

By default attachments will not be saved to the database.
If you want all attachments to be saved to the database, just set this to true:

.. code-block:: python

    EMAIL_LOG_SAVE_ATTACHMENTS = True

And using this setting you can configure path to your attachments:

.. code-block:: python

    EMAIL_LOG_ATTACHMENTS_PATH = "path/to/attachments"

Or you can even provide callable object just like for `FileField.upload_to`

.. code-block:: python

    def get_path(instance, filename):
        date_sent = email.date_sent.strftime('%m-%d-%Y')
        return f"path/to/attachments/{date_sent}/{filename}"

    EMAIL_LOG_ATTACHMENTS_PATH = get_path

If you use `django-anymail`_ then django-email-log can use Anymail signals to
log updates from the configured ESP. If you wish to use this feature, you must
set:

.. code-block:: python

    EMAIL_LOG_CONNECT_ANYMAIL_SIGNALS = True

in your project's `settings.py`. This setting may change in a future version of
django-email-log, so if you do not wish to use Anymail signals you should
explicitly set this to `False`:

.. code-block:: python

    EMAIL_LOG_CONNECT_ANYMAIL_SIGNALS = False

.. _django-anymail: https://github.com/anymail/django-anymail


Using with other email backends
-------------------------------

By default django-email-log uses Django's SMTP backend to send emails.  The
``EMAIL_LOG_BACKEND`` setting should be specified if you are using a custom
email backend.  For example:

.. code-block:: python

    EMAIL_LOG_BACKEND = 'yourapp.backends.YourCustomEmailBackend'

If you are using an email queueing backend such as `django-celery-email`_, the
django-email-log backend should be used behind the queuing backend so errors
will be logged properly.  For example with django-celery-email this should
work:

.. code-block:: python

    CELERY_EMAIL_BACKEND = 'email_log.backends.EmailBackend'

.. _django-celery-email: https://github.com/pmclanahan/django-celery-email
