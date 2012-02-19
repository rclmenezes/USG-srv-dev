from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    url(r'^/?$', 'my.views.getPage', name="home", kwargs={'orderNo': None}),
    url(r'^page/(?P<orderNo>\d)/?$', 'my.views.getPage', name="home"),
    url(r'^addMyApp/(?P<orderNo>\d)/(?P<colID>\w)/?$', 'my.views.addMyApp', name="addMyApp"),
    url(r'^addMyApp/?$', 'my.views.addMyApp', name="addMyApp", kwargs={'orderNo': None, 'colID': None}),
    url(r'^confirmMyApps/(?P<orderNo>\d)/(?P<colID>\w)/?$', 'my.views.confirmMyApps', name="confirmMyApps"),
    url(r'^addPage/?$', 'my.views.addPage', name="addPage"),
    url(r'^loading/?$', 'my.views.loading', name="loading"),
    url(r'^myapps/(?P<relationID>\d+)/?$', 'myapps.views.get_myapp', name="get_myapp"),
    url(r'^refreshApps/?$', 'my.views.refreshApps', name="refreshApps"),
    url(r'^removePage/?$', 'my.views.removePage', name="removePage"),
    url(r'^saveMyApps/(?P<orderNo>\d)/?$', 'my.views.saveMyApps', name="saveMyApps"),
    url(r'^proxy/?$', 'my.views.proxy', name="proxy"),
    url(r'^changePageName/(?P<orderNo>\d)/?$', 'my.views.changePageName', name="changePageName"),
    #url(r'^2/?$', 'my.views.home2', name='home2'),
    #url(r'^updatePanels/?$', 'index.updatePanels', name='updatePanels'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^login/?$', 'django_cas.views.login'),
    (r'^logout/?$', 'django_cas.views.logout'),
    (r'^admin/', include(admin.site.urls)),
)
