django-email-log
================

Django-email-log is a Django app that logs all outgoing emails to the database.

All emails are logged in an Email model and emails may be viewed from the admin
site.  When an email fails to send the error is noted in the model also.

Django-email-log can also be used with other custom email backends by setting
the ``EMAIL_LOG_BACKEND`` setting to your custom email backend.

.. warning::
    This app should not be used if outgoing emails may contain sensitive
    information that shouldn't be logged in the database!

Contents:

.. toctree::
   :maxdepth: 2

   usage

Visit the project `on Github`_ to view the source, submit issues and pull
requests.

.. _on github: https://github.com/treyhunner/django-email-log
