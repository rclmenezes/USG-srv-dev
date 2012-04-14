from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    
    url(r'^$', 'rooms.views.index'),
    (r'^login/?$', 'django_cas.views.login'),
    (r'^logout/?$', 'django_cas.views.logout'),
    
    # Admin interface
    (r'^admin/?$', include(admin.site.urls)),

    (r'^(\w+)/?$', 'rooms.views.building_scope'),
    (r'^(\w+)/(\w+)/?$', 'rooms.views.room_scope'),

)
