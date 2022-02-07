# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Email",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("from_email", models.TextField(verbose_name="from e-mail")),
                ("recipients", models.TextField(verbose_name="recipients")),
                ("subject", models.TextField(verbose_name="subject")),
                ("body", models.TextField(verbose_name="body")),
                (
                    "ok",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="ok"
                    ),
                ),
                (
                    "date_sent",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="date sent", db_index=True
                    ),
                ),
            ],
            options={
                "ordering": ("-date_sent",),
                "verbose_name": "e-mail",
                "verbose_name_plural": "e-mails",
            },
            bases=(models.Model,),
        ),
    ]
