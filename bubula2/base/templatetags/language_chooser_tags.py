# Mod of django-cms, # Copyright (c) 2008, Batiste Bieler (https://github.com/divio/django-cms/blob/develop/LICENSE)
from classytags.arguments import Argument
from classytags.core import Options
from classytags.helpers import InclusionTag
from django import template
from cms.utils import get_language_from_request

register = template.Library()

@register.tag
class PageWithAppLanguageUrl(InclusionTag):
    """
    Displays the url of the current page in the defined language.
    You can set a language_changer function with the set_language_changer function in the utils.py if there is no page.
    This is needed if you have slugs in more than one language.
    Mod: Include any extra part of url made by app.
    """
    name = 'page_with_app_language_url'
    template = 'cms/content.html'
    
    options = Options(
        Argument('lang'),
    )
    
    def get_context(self, context, lang):
        try:
            # If there's an exception (500), default context_processors may not be called.
            request = context['request']
        except KeyError:
            return {'template': 'cms/content.html'}
        if hasattr(request, "_language_changer"):
            try:
                setattr(request._language_changer, 'request', request)
            except AttributeError:
                pass
            url = "/%s" % lang + request._language_changer(lang)
        else:
            page = request.current_page
            if page == "dummy":
                return {'content': ''}
            try:
                url = page.get_absolute_url(language=lang, fallback=False)
                url = "/" + lang + url
            except:
                # no localized path/slug. 
                url = ''
            if page.get_application_urls():
                # determine which part of the current url belongs to the app
                curLang = get_language_from_request(request)
                curPageUrl = page.get_absolute_url(language=curLang, fallback=False)
                curPath = request.path_info
                appPath = curPath[ len(curPageUrl) :]
                url += appPath
        return {'content':url}