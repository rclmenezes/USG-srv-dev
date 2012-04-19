from django.conf.urls.defaults import *
from datetime import date
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

admin.autodiscover()
#today = date.today()

urlpatterns = patterns('',
    # Social
    (r'^club/(?P<club_name>\w+)/?$', 'pam.views.club'),
    url(r'^/?$', 'pam.views.night', kwargs={'day': 0, 'month': 0, 'year': 0}),
    url(r'^fast/?$', 'pam.views.fast', kwargs={'day': 0, 'month': 0, 'year': 0}),
    (r'^login/?', 'django_cas.views.login'),
    (r'^logout/?', 'django_cas.views.logout'),
    (r'^(?P<month>\d+)/(?P<day>\d+)/(?P<year>\d+)/?$', 'pam.views.night'),
    url(r'^fast/(?P<month>\d+)/(?P<day>\d+)/(?P<year>\d+)/?$', 'pam.views.fast'),
    (r'^search$', 'pam.views.search'),
    (r'^event/(?P<event_id>\d+)/?$', 'pam.views.event'),
    (r'^event_edit/(?P<event_id>\d+)/?$', 'pam.views.event_edit'),
    (r'^event_delete/(?P<event_id>\d+)/?$', 'pam.views.event_delete'),
    (r'^event_add/?$', 'pam.views.event_add'),
    (r'^about/?$', 'pam.views.about'),
    
    (r'^login/?$', 'django_cas.views.login'),
    (r'^logout/?$', 'django_cas.views.logout'),
    
    # Admin
    url(r'^admin/?$', 'django_cas.views.login', kwargs={'next_page': '/djadmin/'}),
    (r'^djadmin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()

