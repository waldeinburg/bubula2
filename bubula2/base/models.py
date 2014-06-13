from django.db import models
from hvad.models import TranslatableModel, TranslatedFields
from cms.models.pagemodel import Page

class Subtitle(TranslatableModel):
    page = models.OneToOneField(Page, related_name='subtitle')
    translations = TranslatedFields(
        subtitle = models.CharField(max_length=200)
    )

    def __unicode__(self):
        return self.subtitle