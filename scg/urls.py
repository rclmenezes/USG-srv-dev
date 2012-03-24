from django.conf.urls.defaults import *
import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'views.index'),
    (r'^courses/', include('apps.courses.urls')),
    (r'^reviews/', include('apps.reviews.urls')),
    (r'^students/', include('apps.students.urls')),
    (r'^elearn/', include('apps.elearn.urls')),
    (r'^professors/', include('apps.professors.urls')),

    (r'^about/', 'django.views.generic.simple.direct_to_template', {'template':'static/about.html'}),
    (r'^about/blackboard/', 'django.views.generic.simple.direct_to_template', {'template':'static/boards.html'}),

    (r'^accounts/$', 'django.views.generic.simple.redirect_to', {'url':'login/'}),
    (r'^accounts/login/$', 'django.views.generic.simple.redirect_to', {'url':'/cas/login/'}),
    (r'^accounts/login/secure/$', 'views.login_view'),
    (r'^accounts/profile/$', 'django.views.generic.simple.redirect_to', {'url':'/'}),
    (r'^accounts/logout/$', 'views.logout_view',),

    (r'^cas/login/$', 'views.cas_login'),
    (r'^cas/logout/$', 'views.cas_logout'),

    (r'^scg/$', 'django.views.generic.simple.redirect_to',{'url':'/'}),

    (r'^admin/', include(admin.site.urls)),
    #(r'^admin/(.*)', admin.site.root),

)
