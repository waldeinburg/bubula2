# -*- coding: utf-8 -*-
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _
from comics.shared import get_published_comics

class LatestComicsFeedRSS(Feed):
    title = _(u'Bubula² latest comics')
    link = '/'
    description = _(u'Latest comic of the Bubula² webcomic.')
    description_template = 'comics/feed.html'
    
    def items(self):
        return get_published_comics().order_by('-dateTime')[:5]
    
    def item_title(self, item):
        return item.title

    def item_link(self, item):
        return '/{0}/'.format(item.id)
    
    def item_pubdate(self, item):
        return item.dateTime
    
    
    
class LatestComicsFeedAtom(LatestComicsFeedRSS):
    feed_type = Atom1Feed
    subtitle = LatestComicsFeedRSS.description
