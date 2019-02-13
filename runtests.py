#!/usr/bin/env python
import sys
from os.path import abspath, dirname

import django
from django.conf import settings


sys.path.insert(0, abspath(dirname(__file__)))


if not settings.configured:
    settings.configure(
        INSTALLED_APPS=(
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.auth',
            'django.contrib.admin',
            'django.contrib.messages', # Required for v3+ of Django
            'email_log',
            'email_log.tests',
        ),
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        EMAIL_LOG_BACKEND = 'django.core.mail.backends.locmem.EmailBackend',
        MIDDLEWARE = (
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ),
        ROOT_URLCONF='email_log.tests.urls',
        TEMPLATES = [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [
                ],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.contrib.auth.context_processors.auth',
                        'django.template.context_processors.debug',
                        'django.template.context_processors.i18n',
                        'django.template.context_processors.media',
                        'django.template.context_processors.static',
                        'django.template.context_processors.tz',
                        'django.contrib.messages.context_processors.messages',
                    ],
                },
            },
        ]
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
