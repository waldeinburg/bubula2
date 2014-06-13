from django.http import Http404
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from comics.models import SingleComicPlugin as SingleComicPluginModel
from comics.models import LatestComicPlugin as LatestComicPluginModel
from comics.shared import get_published_comics

class SingleComicPlugin(CMSPluginBase):
    model = SingleComicPluginModel
    name = 'Comics Single'
    render_template = 'comics/plugin/single.html'
    
    # TODO: Change admin so that non-published comics cannot be selected
    # Also, only NormalComic types should be selectable 
    def render(self, context, instance, placeholder):
        if not instance.comic.type == 'NormalComic':
            raise Exception('Only NormalComic type allowed in {0}'.format(self.__class__))
        if not instance.comic.is_published(): # this should not happen
            raise Http404
        context.update({
            'comic': instance.comic
        })
        return context
#plugin_pool.register_plugin(SingleComicPlugin)



class LatestComicPlugin(SingleComicPlugin):
    model = LatestComicPluginModel
    name = 'Comics Latest'

    def render(self, context, instance, placeholder):
        latestSingleInstance = SingleComicPluginModel()
        latestSingleInstance.comic = get_published_comics().order_by('-dateTime')[0]
        latestSingleInstance.showNavigation = instance.showNavigation
        return super(LatestComicPlugin, self).render(context, latestSingleInstance, placeholder)
#plugin_pool.register_plugin(LatestComicPlugin)