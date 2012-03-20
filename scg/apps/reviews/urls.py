from django.conf.urls.defaults import *

urlpatterns = patterns('',
     (r'^post/$', 'apps.reviews.views.post_review'),
     (r'^course/(?P<cid>[0-9]+)/$', 'apps.reviews.views.course_reviews'),
     (r'^professor/(?P<pid>[0-9]+)/$', 'apps.reviews.views.professor_reviews'),
)
