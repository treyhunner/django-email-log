# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email_log', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='email',
            options={'ordering': ('-date_sent',), 'verbose_name_plural': 'emails', 'verbose_name': 'email'},
        ),
        migrations.AlterField(
            model_name='email',
            name='from_email',
            field=models.TextField(verbose_name='from email'),
        ),
    ]
