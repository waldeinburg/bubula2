from datetime import datetime, date, timedelta, time
from django.db import models
from django.utils.translation import ugettext_lazy as _
from hvad.models import TranslatableModel, TranslatedFields
from cms.models import CMSPlugin as CMSPluginModel
import comics.specials

# Comic must be a TranslatableModel even though only its child objects has
# translations, because we cannot make an Admin for it otherwise.
class Comic(TranslatableModel):
    TYPE_CHOICES = []
    # publication default: tomorrow at 6 AM
    # FIXME: this code is run when server is started, not each time admin is loaded. Therefore it does not work.
    dateTime = models.DateTimeField('Publication time', default=datetime.combine( date.today() + timedelta(1), time(6) ))
    
    translations = TranslatedFields(
        title = models.CharField(max_length=200), # title of the comic. Relevant for all types because of listing
    )

    @staticmethod
    def add_type(cls):
        Comic.TYPE_CHOICES.append( (cls.__name__, cls._meta.verbose_name) )
        return cls
    
    def get_comic_obj(self):
        return getattr(self, self.type.lower())
    
    def get_image(self):
        return self.get_comic_obj().get_image()
    
    def get_mouseover_text(self):
        return self.get_comic_obj().get_mouseover_text()
    
    def __unicode__(self):
        return u'{0} ({1})'.format( self.id, self.title )

    def get_absolute_url(self):
        return u'/{0}/{1}/'.format(_('comics'), self.id)
        
    def is_published(self):
        return (self.dateTime <= datetime.now())

    

class ComicTypeModel(models.Model):
    class Meta:
        abstract = True
    
    comic = models.OneToOneField(Comic)

    def __unicode__(self):
        return self.comic.title
    
    # for feeds
    def get_image(self):
        raise NotImplementedError
    
    def get_mouseover_text(self):
        return self.mouseoverText



class ComicInfo(TranslatableModel):
    comic = models.OneToOneField(Comic, related_name='info')
    
    translations = TranslatedFields(
        content = models.TextField()
    )



# django-hvad does not support abstract classes; this way we can "inherit" common fields anyway
class StandardComicTranslatedFields(TranslatedFields):
    def __init__(self, **fields):
        super(StandardComicTranslatedFields, self).__init__(
            pageSubtitle = models.CharField('Page subtitle', max_length=200), # subtitle of the page (easter egg)
            mouseoverText = models.CharField('Mouseover text', max_length=500),
            **fields
        )



@Comic.add_type
class NormalComic(TranslatableModel, ComicTypeModel):
    translations = StandardComicTranslatedFields(
        image = models.ImageField('Image file', upload_to='comics')
    )
    
    def get_image(self):
        return self.image



@Comic.add_type
class ScriptedComic(TranslatableModel, ComicTypeModel):
    translations = StandardComicTranslatedFields()

    def get_image(self):
        return self.images.using_translations().order_by('image')[0].image
    
    

class ComicImageFile(TranslatableModel):
    scriptedComic = models.ForeignKey(ScriptedComic, related_name='images')
    
    translations = TranslatedFields(
        image = models.ImageField('Image file', upload_to='comics')
    )



class ComicScriptFile(TranslatableModel):
    scriptedComic = models.ForeignKey(ScriptedComic, related_name='scripts')
    translations = TranslatedFields(
        file = models.FileField('Script file', upload_to='comics/scripts')
    )



class ComicCSSFile(TranslatableModel):
    scriptedComic = models.ForeignKey(ScriptedComic, related_name='styles')
    translations = TranslatedFields(
        file = models.FileField('CSS file', upload_to='comics/css')
    )



@Comic.add_type
class SpecialPageComic(TranslatableModel, ComicTypeModel):
    klass = models.CharField('Class', max_length=30)
    
    translations = TranslatedFields()
    
    def get_class(self):
        return getattr(comics.specials, self.klass)
    
    def view(self):
        return self.get_class().view()
    
    def get_image(self):
        return self.get_class().get_image()
    
    def get_mouseover_text(self):
        return self.get_class().get_mouseover_text()


# All types added. Now create field
# If this is done in the decorator we get "duplicate field" error on syncdb
Comic.add_to_class( 'type', models.CharField(max_length=30, choices=Comic.TYPE_CHOICES, default=Comic.TYPE_CHOICES[0][0]) )


#
# Plugins
#

class SingleComicPluginBase(CMSPluginModel):
    class Meta:
        abstract = True

    showTitle = models.BooleanField('Show comic title', default=False)



class SingleComicPlugin(SingleComicPluginBase):
    comic = models.ForeignKey('comics.Comic', related_name='plugins')

    def __unicode__(self):
        return self.comic.__unicode__()



# If single and latest need to share some elements, then make a CMSPluginModel base class in another module
class LatestComicPlugin(SingleComicPluginBase):
    def __unicode__(self):
        return 'Latest comic'
