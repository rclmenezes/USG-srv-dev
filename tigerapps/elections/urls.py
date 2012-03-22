from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^/?$', 'elections.views.home', name='home'),
    (r'^login/?', 'django_cas.views.login'),
    (r'^logout/?', 'django_cas.views.logout'),
    (r'^remove/?$', 'elections.views.remove'),
    #(r'^runoff/?$', 'elections.views.runoff'),
    url(r'^register/?$', 'elections.views.signup', kwargs={'election': None}),
    url(r'^statements/?$', 'elections.views.statements', name='statements'),
    (r'^robots\.txt$', direct_to_template,
         {'template': 'robots.txt', 'mimetype': 'text/plain'}),
    # Example:
    # (r'^register/', include('register.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)