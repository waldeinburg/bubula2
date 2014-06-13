from django.contrib import admin
from hvad.admin import TranslatableAdmin
from cms.admin.placeholderadmin import PlaceholderAdmin
from hvadcontentblock.models import ContentBlock

class ContentBlockAdmin(TranslatableAdmin, PlaceholderAdmin):
    pass
admin.site.register(ContentBlock, ContentBlockAdmin)