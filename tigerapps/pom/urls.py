from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # TigerTrade
    url(r'^/?(\d*)/?$', 'pom.views.index'),
)
