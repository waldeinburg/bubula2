from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('comics.views',
    url(r'^$', 'index'),
)