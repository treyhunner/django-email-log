# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('from_email', models.TextField(verbose_name=u'from e-mail')),
                ('recipients', models.TextField(verbose_name=u'recipients')),
                ('subject', models.TextField(verbose_name=u'subject')),
                ('body', models.TextField(verbose_name=u'body')),
                ('ok', models.BooleanField(default=False, db_index=True, verbose_name=u'ok')),
                ('date_sent', models.DateTimeField(auto_now_add=True, verbose_name=u'date sent', db_index=True)),
            ],
            options={
                u'ordering': (u'-date_sent',),
                u'verbose_name': u'e-mail',
                u'verbose_name_plural': u'e-mails',
            },
            bases=(models.Model,),
        ),
    ]
