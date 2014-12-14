from django import forms
from django.contrib import admin
from hvad.admin import TranslatableAdmin, TranslatableStackedInline, InlineModelForm
from copyhvadfilefield.adminhelper import dajaxiceScript, copyhvadfilefieldScript
from copyhvadfilefield.register import register_translation_with_file_field_models
from comics.models import Comic, ComicInfo, NormalComic, ScriptedComic, ComicImageFile, ComicScriptFile, ComicCSSFile
import comics.models

register_translation_with_file_field_models(
    NormalComic,
    ComicImageFile,
    ComicScriptFile,
    ComicCSSFile
)



class ComicInfoForm(InlineModelForm):
    class Meta:
        model = ComicInfo

    content = forms.CharField(widget=forms.Textarea, help_text='Markdown')
    


class ComicInfoInline(TranslatableStackedInline):
    model = ComicInfo
    form = ComicInfoForm
    extra = 0
    


class ComicAdmin(TranslatableAdmin):
    class Media:
        css = {'all': ('comics/css/admin/comicadmin.css',)}
        js = ('comics/js/admin/comicadmin.js', dajaxiceScript, copyhvadfilefieldScript)
    
    date_hierarchy = 'dateTime'
    list_display = ('get_title', 'id', 'dateTime', 'type')

    # until list_display is properly implemented in TranslatableAdmin
    def get_title(self, obj):
        return obj.title
    get_title.short_description = 'Title'

#    def get_type(self, obj):
#        return capfirst( getattr(comics.models, obj.type)._meta.verbose_name ) # hack; accessing private member
#    get_type.short_description = 'Type'
    
    inlines = []
    for comicType in Comic.TYPE_CHOICES:
        T = type(
            '{0}Inline'.format(comicType[0]),
            (TranslatableStackedInline,),
            {'model': getattr(comics.models, comicType[0])}
        )
        inlines.append(T)
    inlines.append(ComicInfoInline)
admin.site.register(Comic, ComicAdmin)



class ComicImageFileAdmin(TranslatableStackedInline):
    model = ComicImageFile
    extra = 1



class ComicScriptFileAdmin(TranslatableStackedInline):
    model = ComicScriptFile
    extra = 1



class ComicCSSFileAdmin(TranslatableStackedInline):
    model = ComicCSSFile
    extra = 0



class ScriptedComicAdmin(TranslatableAdmin):
    class Media:
        js = ('comics/js/admin/scriptcomicfilefieldmodels.js', dajaxiceScript, copyhvadfilefieldScript)

    exclude = ('comic',)
    inlines = (ComicImageFileAdmin, ComicScriptFileAdmin, ComicCSSFileAdmin)
    
    def has_add_permission(self, request):
        return False
admin.site.register(ScriptedComic, ScriptedComicAdmin)
