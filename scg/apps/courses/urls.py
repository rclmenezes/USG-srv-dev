from django.conf.urls.defaults import *

urlpatterns = patterns('',
     (r'^dr/(?P<dr>[A-Z]+)/$', 'apps.courses.views.dr'),
     (r'^dept/(?P<dept>[A-Z]+)/$', 'apps.courses.views.dept'),
     (r'^search/$', 'apps.courses.views.search'),
     (r'^(?P<cid>\d+)/$', 'apps.courses.views.course_detail'),
     (r'^(?P<cid>\d+)/blackboard/$', 'apps.courses.views.blackboard'),
     (r'^api/(?P<dep>.+)-(?P<num>\d+)\.json', 'apps.courses.api.course'),
     (r'^$', 'django.views.generic.simple.redirect_to',{'url':'/'}),
)
