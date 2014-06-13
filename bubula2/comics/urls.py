from django.conf.urls.defaults import patterns, url
from django.views.generic.list import ListView
from comics.feeds import LatestComicsFeedRSS, LatestComicsFeedAtom
from comics.shared import get_published_comics

urlpatterns = patterns('comics.views',
    url(r'^(?P<comicId>\d+)/$', 'single'),
    url(r'^(?P<dateStr>[0-3]\d-[01]\d-\d{4})/', 'single_by_date'), # the regexp handles the worst cases of invalid dates
    url(r'^random/$', 'random'),
    url( r'^feed/latest/rss/$', LatestComicsFeedRSS() ),
    url( r'^feed/latest/atom/$', LatestComicsFeedAtom() ),
    url( r'^$', ListView.as_view( queryset=get_published_comics().order_by('-dateTime') ) ), #'archive'),
)