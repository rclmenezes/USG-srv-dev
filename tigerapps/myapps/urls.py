from django.conf.urls.defaults import *
from adminsites import moviesAdmin

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^usgmovies/', include(moviesAdmin.urls)),
)