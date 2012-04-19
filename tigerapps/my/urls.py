from django.conf.urls.defaults import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^/?$', 'my.views.getPage', name="home", kwargs={'orderNo': None}),
    url(r'^page/(?P<orderNo>\d)/?$', 'my.views.getPage', name="home"),
    url(r'^addMyApp/(?P<orderNo>\d)/(?P<colID>\w)/?$', 'my.views.addMyApp', name="addMyApp"),
    url(r'^addMyApp/?$', 'my.views.addMyApp', name="addMyApp", kwargs={'orderNo': None, 'colID': None}),
    url(r'^confirmMyApps/(?P<orderNo>\d)/(?P<colID>\w)/?$', 'my.views.confirmMyApps', name="confirmMyApps"),
    url(r'^addPage/?$', 'my.views.addPage', name="addPage"),
    url(r'^loading/?$', 'my.views.loading', name="loading"),
    url(r'^(?P<relationID>\d+)/(?P<location>\w+)/?$', 'myapps.views.get_myapp', name="get_myapp", kwargs={'settings': False}),
    url(r'^(?P<relationID>\d+)/(?P<location>\w+)/settings/?$', 'myapps.views.get_myapp', name="get_myapp", kwargs={'settings': True}),
    url(r'^refreshApps/?$', 'my.views.refreshApps', name="refreshApps"),
    url(r'^removePage/?$', 'my.views.removePage', name="removePage"),
    url(r'^saveMyApps/(?P<orderNo>\d)/?$', 'my.views.saveMyApps', name="saveMyApps"),
    url(r'^proxy/?$', 'my.views.proxy', name="proxy"),
    url(r'^changePageName/(?P<orderNo>\d)/?$', 'my.views.changePageName', name="changePageName"),
    #url(r'^2/?$', 'my.views.home2', name='home2'),
    #url(r'^updatePanels/?$', 'index.updatePanels', name='updatePanels'),

    (r'^login/?$', 'django_cas.views.login'),
    (r'^logout/?$', 'django_cas.views.logout'),

    # Admin
    url(r'^admin/?$', 'django_cas.views.login', kwargs={'next_page': '/djadmin/'}),
    (r'^djadmin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()

