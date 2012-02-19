from django.conf.urls.defaults import *
from views import *
from auth import login

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
 
urlpatterns = patterns('',
    # Example:
    # (r'^newfacebook/', include('newfacebook.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    
    (r'^$',home),
    (r'^p/(?P<netid>.*)$',profile),
    (r'^p/(?P<netid>.*)/edit$',profileEdit),
    (r'^search$',search),
    (r'^toolshed$',toolshed),
    (r'^autocomplete/(?P<fieldname>.*)',autocomplete),
    (r'^login$',login),
    (r'^logout$',logout),
    
    #(r'^p/(?P<netid>.*)/photo$',photoEdit),
    
)
