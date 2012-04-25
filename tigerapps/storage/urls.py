from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template 
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^/?$', 'storage.views.home'),
    url(r'^register/?$', 'storage.views.register'),
    url(r'^register/complete/?$', 'storage.views.register_complete'),
    url(r'^status/?$', 'storage.views.status'),
    
    (r'^login/?$', 'django_cas.views.login'),
    (r'^logout/?$', 'django_cas.views.logout'),
    
    (r'^paypal/ipntesturl123/?$', 'storage.views.my_ipn'),

    #Example
    #url(r'^bldg/(?P<bldg_id>\S+)/?$', 'pom.views.map_bldg_clicked'),

    # Admin
    url(r'^admin/?$', 'django_cas.views.login', kwargs={'next_page': '/djadmin/'}),
    (r'^djadmin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()

