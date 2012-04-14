from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    
    url(r'^$', 'rooms.views.index'),
    (r'^login/?$', 'django_cas.views.login'),
    (r'^logout/?$', 'django_cas.views.logout'),
    (r'^drawid/(?P<drawid>\d{1})$', 'rooms.views.draw'),
    # Admin interface
    (r'^admin/', include(admin.site.urls)),
)