from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Map-related
    url(r'^/?$', direct_to_template,
        {'template': 'pom/index.html'}),
    url(r'^bldg/(?P<bldg_id>\S+)/?$', 'pom.views.map_bldg_clicked'),
    
    url(r'^pmap/?$', direct_to_template,
        {'template': 'pom/pmap.html'}),

    #Admin
    url(r'^admin/?$', 'django_cas.views.login', kwargs={'next_page': '/djadmin/'}),
    (r'^djadmin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()

