from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    
    url(r'^$', 'rooms.views.index'),
    (r'^login/?$', 'django_cas.views.login'),
    (r'^logout/?$', 'django_cas.views.logout'),
    (r'^drawid/(?P<drawid>\d{1})$', 'rooms.views.draw'),
    (r'^create_queue/(?P<drawid>\d{1})$', 'rooms.views.create_queue'),
    (r'^get_queue/(?P<drawid>\d{1})$', 'rooms.views.get_queue'),
    (r'^update_queue/(?P<drawid>\d{1})$', 'rooms.views.update_queue'),
    (r'^get_room/(?P<roomid>\d+)', 'rooms.views.get_room'),
    # Admin interface
    (r'^admin/', include(admin.site.urls)),
    
    #for testing purposes
    (r'^review/(?P<roomid>\d+)$', 'rooms.views.review'),
    (r'^usersettings.html$','rooms.views.settings')
)
