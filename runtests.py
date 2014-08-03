#!/usr/bin/env python
import sys
from os.path import abspath, dirname

from django.conf import settings
import django


sys.path.insert(0, abspath(dirname(__file__)))


if not settings.configured:
    settings.configure(
        INSTALLED_APPS=(
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.auth',
            'django.contrib.admin',
            'email_log',
            'email_log.tests',
        ),
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        EMAIL_LOG_BACKEND = 'django.core.mail.backends.locmem.EmailBackend',
        ROOT_URLCONF='email_log.tests.urls',
    )


def runtests():
    if hasattr(django, 'setup'):
        django.setup()
    try:
        from django.test.runner import DiscoverRunner
        runner_class = DiscoverRunner
        test_args = ['email_log.tests']
    except ImportError:
        from django.test.simple import DjangoTestSuiteRunner
        runner_class = DjangoTestSuiteRunner
        test_args = ['tests']

    failures = runner_class(failfast=False).run_tests(test_args)
    sys.exit(failures)


if __name__ == "__main__":
    runtests()
