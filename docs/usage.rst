Usage
=====

Installation
------------

Install from PyPI:

.. code-block:: bash

    $ pip install django-email-log


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
