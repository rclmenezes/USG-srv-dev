from django.conf.urls.defaults import *
from adminsites import moviesAdmin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^usgmovies/', include(moviesAdmin.urls)),
    url(r'^proxy/?$', 'my.views.proxy', name="proxy"),
    
    url(r'^(?P<relationID>\d+)/(?P<location>\w+)/?$', 'myapps.views.get_myapp', name="get_myapp", kwargs={'settings': False}),
    url(r'^(?P<relationID>\d+)/(?P<location>\w+)/settings/?$', 'myapps.views.get_myapp', name="get_myapp", kwargs={'settings': True}),

    (r'^login/?$', 'django_cas.views.login'),
    (r'^logout/?$', 'django_cas.views.logout'),

    # Admin
    url(r'^admin/?$', 'django_cas.views.login', kwargs={'next_page': '/djadmin/'}),
    (r'^djadmin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()

