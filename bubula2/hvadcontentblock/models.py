from django.db import models
#from cms.models.fields import PlaceholderField
#from django.utils.translation import ugettext_lazy as _
from hvad.models import TranslatableModel, TranslatedFields

# requires hack
# https://github.com/nephila/django-hvad/commit/8ec407d998aa54f297c74c3a9d89bd75d1f56a38
class ContentBlock(TranslatableModel):
    code = models.CharField(max_length=255, unique=True, db_index=True, primary_key=True)
    name = models.CharField(max_length=255, blank=True, default='')
    translations = TranslatedFields(
        raw = models.TextField(blank=True)
#        content = PlaceholderField(slotname='content',
#                                   verbose_name=_('content'))
    )
    
    def __unicode__(self):
        return self.name if self.name else self.code 