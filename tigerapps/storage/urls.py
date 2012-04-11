from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import direct_to_template 
admin.autodiscover()

urlpatterns = patterns('',
    # Map-related
    url(r'^/?$', direct_to_template,
        {'template': 'storage/index.html'}),
    url(r'^paypal/$', 'storage.views.paypal', name='paypal'),
#    url(r'^bldg/(?P<bldg_id>\S+)/?$', 'pom.views.map_bldg_clicked'),

    url(r'^admin/', include(admin.site.urls)),
)
