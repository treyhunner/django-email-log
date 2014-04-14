import os

default_app_config = 'email_log.apps.EmailLogConfig'

current_dir = os.path.dirname(__file__)


# Ensure the user is not using Django 1.6 or below with South
try:
    from django.db import migrations  # noqa
except ImportError:
    migrations_dir = os.path.join(current_dir, 'south')
else:
    migrations_dir = os.path.join(current_dir, 'nonsouth')

__path__.append(migrations_dir)
