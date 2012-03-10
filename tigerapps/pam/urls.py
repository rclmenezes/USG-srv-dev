from django.conf.urls.defaults import *
from django.contrib import admin
from datetime import date


admin.autodiscover()
today = date.today()

urlpatterns = patterns('',
    # Social
    (r'^club/(?P<club_name>\w+)/?$', 'pam.views.club'),
    url(r'^/?$', 'pam.views.night', kwargs={'day': today.day, 'month': today.month, 'year': today.year}),
    url(r'^fast/?$', 'pam.views.fast', kwargs={'day': today.day, 'month': today.month, 'year': today.year}),
    (r'^login/?', 'django_cas.views.login'),
    (r'^logout/?', 'django_cas.views.logout'),
    (r'^(?P<month>\d+)/(?P<day>\d+)/(?P<year>\d+)/?$', 'pam.views.night'),
    url(r'^fast/(?P<month>\d+)/(?P<day>\d+)/(?P<year>\d+)/?$', 'pam.views.fast'),
    (r'^search$', 'pam.views.search'),
    (r'^event/(?P<event_id>\d+)/?$', 'pam.views.event'),
    (r'^event_edit/(?P<event_id>\d+)/?$', 'pam.views.event_edit'),
    (r'^event_delete/(?P<event_id>\d+)/?$', 'pam.views.event_delete'),
    (r'^admin/', include(admin.site.urls)),
    (r'^event_add/?$', 'pam.views.event_add'),
    (r'^about/?$', 'pam.views.about'),
    
    # Admin
    (r'^login/?$', 'django_cas.views.login'),
    (r'^logout/?$', 'django_cas.views.logout'),
)

