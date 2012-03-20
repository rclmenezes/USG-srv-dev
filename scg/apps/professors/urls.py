from django.conf.urls.defaults import *

urlpatterns = patterns('',
     (r'^search/$', 'apps.professors.views.search'),
)
