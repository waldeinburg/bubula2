# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ComicTranslation'
        db.create_table('comics_comic_translation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['comics.Comic'])),
        ))
        db.send_create_signal('comics', ['ComicTranslation'])

        # Adding unique constraint on 'ComicTranslation', fields ['language_code', 'master']
        db.create_unique('comics_comic_translation', ['language_code', 'master_id'])

        # Adding model 'Comic'
        db.create_table('comics_comic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dateTime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 10, 7, 0, 0))),
            ('type', self.gf('django.db.models.fields.CharField')(default='NormalComic', max_length=30)),
        ))
        db.send_create_signal('comics', ['Comic'])

        # Adding model 'NormalComicTranslation'
        db.create_table('comics_normalcomic_translation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('pageSubtitle', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('mouseoverText', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['comics.NormalComic'])),
        ))
        db.send_create_signal('comics', ['NormalComicTranslation'])

        # Adding unique constraint on 'NormalComicTranslation', fields ['language_code', 'master']
        db.create_unique('comics_normalcomic_translation', ['language_code', 'master_id'])

        # Adding model 'NormalComic'
        db.create_table('comics_normalcomic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('comic', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['comics.Comic'], unique=True)),
        ))
        db.send_create_signal('comics', ['NormalComic'])

        # Adding model 'ScriptedComicTranslation'
        db.create_table('comics_scriptedcomic_translation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pageSubtitle', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('mouseoverText', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['comics.ScriptedComic'])),
        ))
        db.send_create_signal('comics', ['ScriptedComicTranslation'])

        # Adding unique constraint on 'ScriptedComicTranslation', fields ['language_code', 'master']
        db.create_unique('comics_scriptedcomic_translation', ['language_code', 'master_id'])

        # Adding model 'ScriptedComic'
        db.create_table('comics_scriptedcomic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('comic', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['comics.Comic'], unique=True)),
        ))
        db.send_create_signal('comics', ['ScriptedComic'])

        # Adding model 'ComicImageFileTranslation'
        db.create_table('comics_comicimagefile_translation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['comics.ComicImageFile'])),
        ))
        db.send_create_signal('comics', ['ComicImageFileTranslation'])

        # Adding unique constraint on 'ComicImageFileTranslation', fields ['language_code', 'master']
        db.create_unique('comics_comicimagefile_translation', ['language_code', 'master_id'])

        # Adding model 'ComicImageFile'
        db.create_table('comics_comicimagefile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scriptedComic', self.gf('django.db.models.fields.related.ForeignKey')(related_name='images', to=orm['comics.ScriptedComic'])),
        ))
        db.send_create_signal('comics', ['ComicImageFile'])

        # Adding model 'ComicScriptFileTranslation'
        db.create_table('comics_comicscriptfile_translation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['comics.ComicScriptFile'])),
        ))
        db.send_create_signal('comics', ['ComicScriptFileTranslation'])

        # Adding unique constraint on 'ComicScriptFileTranslation', fields ['language_code', 'master']
        db.create_unique('comics_comicscriptfile_translation', ['language_code', 'master_id'])

        # Adding model 'ComicScriptFile'
        db.create_table('comics_comicscriptfile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scriptedComic', self.gf('django.db.models.fields.related.ForeignKey')(related_name='scripts', to=orm['comics.ScriptedComic'])),
        ))
        db.send_create_signal('comics', ['ComicScriptFile'])

        # Adding model 'ComicCSSFileTranslation'
        db.create_table('comics_comiccssfile_translation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['comics.ComicCSSFile'])),
        ))
        db.send_create_signal('comics', ['ComicCSSFileTranslation'])

        # Adding unique constraint on 'ComicCSSFileTranslation', fields ['language_code', 'master']
        db.create_unique('comics_comiccssfile_translation', ['language_code', 'master_id'])

        # Adding model 'ComicCSSFile'
        db.create_table('comics_comiccssfile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scriptedComic', self.gf('django.db.models.fields.related.ForeignKey')(related_name='styles', to=orm['comics.ScriptedComic'])),
        ))
        db.send_create_signal('comics', ['ComicCSSFile'])

        # Adding model 'SpecialPageComicTranslation'
        db.create_table('comics_specialpagecomic_translation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['comics.SpecialPageComic'])),
        ))
        db.send_create_signal('comics', ['SpecialPageComicTranslation'])

        # Adding unique constraint on 'SpecialPageComicTranslation', fields ['language_code', 'master']
        db.create_unique('comics_specialpagecomic_translation', ['language_code', 'master_id'])

        # Adding model 'SpecialPageComic'
        db.create_table('comics_specialpagecomic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('comic', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['comics.Comic'], unique=True)),
            ('klass', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('comics', ['SpecialPageComic'])

        # Adding model 'SingleComicPlugin'
        db.create_table('cmsplugin_singlecomicplugin', (
            ('cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('showTitle', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('comic', self.gf('django.db.models.fields.related.ForeignKey')(related_name='plugins', to=orm['comics.Comic'])),
        ))
        db.send_create_signal('comics', ['SingleComicPlugin'])

        # Adding model 'LatestComicPlugin'
        db.create_table('cmsplugin_latestcomicplugin', (
            ('cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('showTitle', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('comics', ['LatestComicPlugin'])


    def backwards(self, orm):
        # Removing unique constraint on 'SpecialPageComicTranslation', fields ['language_code', 'master']
        db.delete_unique('comics_specialpagecomic_translation', ['language_code', 'master_id'])

        # Removing unique constraint on 'ComicCSSFileTranslation', fields ['language_code', 'master']
        db.delete_unique('comics_comiccssfile_translation', ['language_code', 'master_id'])

        # Removing unique constraint on 'ComicScriptFileTranslation', fields ['language_code', 'master']
        db.delete_unique('comics_comicscriptfile_translation', ['language_code', 'master_id'])

        # Removing unique constraint on 'ComicImageFileTranslation', fields ['language_code', 'master']
        db.delete_unique('comics_comicimagefile_translation', ['language_code', 'master_id'])

        # Removing unique constraint on 'ScriptedComicTranslation', fields ['language_code', 'master']
        db.delete_unique('comics_scriptedcomic_translation', ['language_code', 'master_id'])

        # Removing unique constraint on 'NormalComicTranslation', fields ['language_code', 'master']
        db.delete_unique('comics_normalcomic_translation', ['language_code', 'master_id'])

        # Removing unique constraint on 'ComicTranslation', fields ['language_code', 'master']
        db.delete_unique('comics_comic_translation', ['language_code', 'master_id'])

        # Deleting model 'ComicTranslation'
        db.delete_table('comics_comic_translation')

        # Deleting model 'Comic'
        db.delete_table('comics_comic')

        # Deleting model 'NormalComicTranslation'
        db.delete_table('comics_normalcomic_translation')

        # Deleting model 'NormalComic'
        db.delete_table('comics_normalcomic')

        # Deleting model 'ScriptedComicTranslation'
        db.delete_table('comics_scriptedcomic_translation')

        # Deleting model 'ScriptedComic'
        db.delete_table('comics_scriptedcomic')

        # Deleting model 'ComicImageFileTranslation'
        db.delete_table('comics_comicimagefile_translation')

        # Deleting model 'ComicImageFile'
        db.delete_table('comics_comicimagefile')

        # Deleting model 'ComicScriptFileTranslation'
        db.delete_table('comics_comicscriptfile_translation')

        # Deleting model 'ComicScriptFile'
        db.delete_table('comics_comicscriptfile')

        # Deleting model 'ComicCSSFileTranslation'
        db.delete_table('comics_comiccssfile_translation')

        # Deleting model 'ComicCSSFile'
        db.delete_table('comics_comiccssfile')

        # Deleting model 'SpecialPageComicTranslation'
        db.delete_table('comics_specialpagecomic_translation')

        # Deleting model 'SpecialPageComic'
        db.delete_table('comics_specialpagecomic')

        # Deleting model 'SingleComicPlugin'
        db.delete_table('cmsplugin_singlecomicplugin')

        # Deleting model 'LatestComicPlugin'
        db.delete_table('cmsplugin_latestcomicplugin')


    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 10, 6, 0, 0)'}),
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
            'dateTime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 10, 7, 0, 0)'}),
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