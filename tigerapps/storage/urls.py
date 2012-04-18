from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template 
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^/?$', direct_to_template,
        {'template': 'storage/index.html'}),
    #Example
    #url(r'^bldg/(?P<bldg_id>\S+)/?$', 'pom.views.map_bldg_clicked'),


    # Paypal
    url(r'^paypal/$', 'storage.views.product_detail', name='paypal'),
    (r'^paypal/ipn/', include('paypal.standard.ipn.urls')),

    # Admin
    url(r'^admin/?$', 'django_cas.views.login', kwargs={'next_page': '/djadmin/'}),
    (r'^djadmin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()

