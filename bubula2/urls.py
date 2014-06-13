from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import RedirectView
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
admin.autodiscover()
dajaxice_autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # redirect /# to /comics/#. Because the base template relies on cms we can't use comics.view.single directly
    url(r'^(?P<comicId>\d+)/$', 'comics.views.single_redirect'),
    url(r'^(?P<dateStr>[0-3]\d-[01]\d-\d{4})/', RedirectView.as_view(url='/comics/%(dateStr)s')),
    url(r'^admin/', include(admin.site.urls)),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    url(r'^', include('cms.urls')),
)

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns = patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url(r'', include('django.contrib.staticfiles.urls')),
    ) + urlpatterns