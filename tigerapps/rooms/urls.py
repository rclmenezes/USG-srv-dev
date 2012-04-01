from django.conf.urls.defaults import *
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    
    url(r'^$', 'rooms.views.index'),
    # Admin
    (r'^login/?$', 'django_cas.views.login'),
    (r'^logout/?$', 'django_cas.views.logout'),
    
    # Try to find a post called that
#    (r'^admin/', include(admin.site.urls)),
)
