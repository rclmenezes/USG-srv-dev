from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import direct_to_template 
admin.autodiscover()

urlpatterns = patterns('',
    # Map-related
    url(r'^/?$', direct_to_template,
        {'template': 'pom/index.html'}),
    url(r'^bldg/(?P<bldg_id>\S+)/?$', 'pom.views.map_bldg_clicked'),
    
    url(r'^pmap/?$', direct_to_template,
        {'template': 'pom/pmap.html'}),
)
