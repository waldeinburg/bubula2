from django.contrib import admin
from hvad.admin import TranslatableStackedInline
from cms.models.pagemodel import Page
from cms.admin.pageadmin import PageAdmin
from base.models import Subtitle

class SubtitleAdmin(TranslatableStackedInline):
    template = 'base/admin/editpagesubtitle.html'
    model = Subtitle

PageAdmin.inlines.append(SubtitleAdmin)

admin.site.unregister(Page)
admin.site.register(Page, PageAdmin)