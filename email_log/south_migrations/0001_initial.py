# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Email'
        db.create_table(u'email_log_email', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_email', self.gf('django.db.models.fields.TextField')()),
            ('recipients', self.gf('django.db.models.fields.TextField')()),
            ('subject', self.gf('django.db.models.fields.TextField')()),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('ok', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('date_sent', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
        ))
        db.send_create_signal(u'email_log', ['Email'])


    def backwards(self, orm):
        # Deleting model 'Email'
        db.delete_table(u'email_log_email')


    models = {
        u'email_log.email': {
            'Meta': {'ordering': "(u'-date_sent',)", 'object_name': 'Email'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'date_sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'from_email': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ok': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'recipients': ('django.db.models.fields.TextField', [], {}),
            'subject': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['email_log']