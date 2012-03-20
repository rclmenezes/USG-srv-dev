from django.conf.urls.defaults import *

urlpatterns = patterns('',
     (r'^add_mycourse/(?P<cid>[0-9]+)/(?P<semester>[SF])/(?P<year>[0-9]+)/$', 'apps.students.views.add_mycourse'),
     (r'^email_courses/(?P<semester>[SF])/(?P<year>[0-9]{4})/$', 'apps.students.views.email_courses_for_term'),
     (r'^remove_mycourse/(?P<id>[0-9]+)/$', 'apps.students.views.remove_mycourse'),
     (r'^mysections/add/(?P<sid>[0-9]+)/$', 'apps.students.views.add_mysection'),

     (r'^class_roster/(?P<cid>[0-9]+)/$', 'apps.students.views.class_roster'),
)
