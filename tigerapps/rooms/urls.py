from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    
    url(r'^$', 'rooms.views.index'),
    (r'^login/?$', 'django_cas.views.login'),
    (r'^logout/?$', 'django_cas.views.logout'),
    (r'^drawid/(?P<drawid>\d{1})$', 'rooms.views.draw'),
    (r'^create_queue/(?P<drawid>\d{1})$', 'rooms.views.create_queue'),
    (r'^invite_queue/?$', 'rooms.views.invite_queue'),
    (r'^respond_queue/?$', 'rooms.views.respond_queue'),
    (r'^leave_queue/?$', 'rooms.views.leave_queue'),
    (r'^get_room/(?P<roomid>\d+)', 'rooms.views.get_room'),
    # Admin interface
    (r'^admin/', include(admin.site.urls)),
    
    #for testing purposes
    #(r'^review/(?P<roomid>\d+)$', 'rooms.views.review'),
    
    (r'^test','rooms.views.test'),
    (r'^trigger','rooms.views.trigger'),
    (r'^user_settings.html$','rooms.views.settings'),
    (r'^confirm_phone.html$','rooms.views.confirm_phone'),
    (r'^manage_queues.html$','rooms.views.manage_queues'),

    # Real-time requests
    (r'^update_queue/(?P<drawid>\d{1})$', 'rooms.views.update_queue'),
    (r'^get_queue/(?P<drawid>\d{1})$', 'rooms.views.get_queue'),
    (r'^get_queue/(?P<drawid>\d{1})/(?P<timestamp>\d+)$', 'rooms.views.get_queue'),
    (r'^start_simulation/(?P<delay>\d+)$', 'rooms.views.start_simulation'),
    (r'^stop_simulation/?$', 'rooms.views.stop_simulation'),
)
