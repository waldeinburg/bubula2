# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ComicInfo'
        db.create_table('comics_comicinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('comic', self.gf('django.db.models.fields.related.OneToOneField')(related_name='info', unique=True, to=orm['comics.Comic'])),
        ))
        db.send_create_signal('comics', ['ComicInfo'])

        # Adding model 'ComicInfoTranslation'
        db.create_table('comics_comicinfo_translation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['comics.ComicInfo'])),
        ))
        db.send_create_signal('comics', ['ComicInfoTranslation'])

        # Adding unique constraint on 'ComicInfoTranslation', fields ['language_code', 'master']
        db.create_unique('comics_comicinfo_translation', ['language_code', 'master_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'ComicInfoTranslation', fields ['language_code', 'master']
        db.delete_unique('comics_comicinfo_translation', ['language_code', 'master_id'])

        # Deleting model 'ComicInfo'
        db.delete_table('comics_comicinfo')

        # Deleting model 'ComicInfoTranslation'
        db.delete_table('comics_comicinfo_translation')


    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 11, 16, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'comics.comic': {
            'Meta': {'object_name': 'Comic'},
            'dateTime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 11, 17, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'NormalComic'", 'max_length': '30'})
        },
        'comics.comiccssfile': {
            'Meta': {'object_name': 'ComicCSSFile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scriptedComic': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'styles'", 'to': "orm['comics.ScriptedComic']"})
        },
        'comics.comiccssfiletranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'ComicCSSFileTranslation', 'db_table': "'comics_comiccssfile_translation'"},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': "orm['comics.ComicCSSFile']"})
        },
        'comics.comicimagefile': {
            'Meta': {'object_name': 'ComicImageFile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scriptedComic': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': "orm['comics.ScriptedComic']"})
        },
        'comics.comicimagefiletranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'ComicImageFileTranslation', 'db_table': "'comics_comicimagefile_translation'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': "orm['comics.ComicImageFile']"})
        },
        'comics.comicinfo': {
            'Meta': {'object_name': 'ComicInfo'},
            'comic': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'info'", 'unique': 'True', 'to': "orm['comics.Comic']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'comics.comicinfotranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'ComicInfoTranslation', 'db_table': "'comics_comicinfo_translation'"},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': "orm['comics.ComicInfo']"})
        },
        'comics.comicscriptfile': {
            'Meta': {'object_name': 'ComicScriptFile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scriptedComic': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'scripts'", 'to': "orm['comics.ScriptedComic']"})
        },
        'comics.comicscriptfiletranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'ComicScriptFileTranslation', 'db_table': "'comics_comicscriptfile_translation'"},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': "orm['comics.ComicScriptFile']"})
        },
        'comics.comictranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'ComicTranslation', 'db_table': "'comics_comic_translation'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': "orm['comics.Comic']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'comics.latestcomicplugin': {
            'Meta': {'object_name': 'LatestComicPlugin', 'db_table': "'cmsplugin_latestcomicplugin'"},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'showTitle': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'comics.normalcomic': {
            'Meta': {'object_name': 'NormalComic'},
            'comic': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['comics.Comic']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'comics.normalcomictranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'NormalComicTranslation', 'db_table': "'comics_normalcomic_translation'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': "orm['comics.NormalComic']"}),
            'mouseoverText': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'pageSubtitle': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'comics.scriptedcomic': {
            'Meta': {'object_name': 'ScriptedComic'},
            'comic': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['comics.Comic']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'comics.scriptedcomictranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'ScriptedComicTranslation', 'db_table': "'comics_scriptedcomic_translation'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': "orm['comics.ScriptedComic']"}),
            'mouseoverText': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'pageSubtitle': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'comics.singlecomicplugin': {
            'Meta': {'object_name': 'SingleComicPlugin', 'db_table': "'cmsplugin_singlecomicplugin'"},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'comic': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'plugins'", 'to': "orm['comics.Comic']"}),
            'showTitle': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'comics.specialpagecomic': {
            'Meta': {'object_name': 'SpecialPageComic'},
            'comic': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['comics.Comic']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'klass': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'comics.specialpagecomictranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'SpecialPageComicTranslation', 'db_table': "'comics_specialpagecomic_translation'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': "orm['comics.SpecialPageComic']"})
        }
    }

    complete_apps = ['comics']