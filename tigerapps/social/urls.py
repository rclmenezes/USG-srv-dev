from django.conf.urls.defaults import *
from django.contrib import admin
from datetime import date
admin.autodiscover()

today = date.today()

urlpatterns = patterns('',
    # Social
    url(r'^/?$', 'social.views.night', kwargs={'day': today.day, 'month': today.month, 'year': today.year}),
    (r'^login/?', 'django_cas.views.login'),
    (r'^logout/?', 'django_cas.views.logout'),
    (r'^(?P<month>\d+)/(?P<day>\d+)/(?P<year>\d+)/$', 'social.views.night'),
    (r'^search$', 'social.views.search'),
    (r'^event/(?P<event_id>\d+)/?$', 'social.views.event'),
    (r'^admin/', include(admin.site.urls)),
    (r'^(?P<club>\w+)/?$', 'social.views.club'),
    
    # Admin
    (r'^login/?$', 'django_cas.views.login'),
    (r'^logout/?$', 'django_cas.views.logout'),
)