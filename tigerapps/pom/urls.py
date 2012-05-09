from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Map-related
    url(r'^/?$', direct_to_template,
        {'template': 'pom/index.html'}),
    url(r'^test/?$', direct_to_template,
        {'template': 'pom/test.html'}),
    
    url(r'^bldgs/filter/?$', 'pom.views.bldgs_for_filter'),
    url(r'^events/bldg/(?P<bldg_code>\S+)/?$', 'pom.views.events_for_bldg'),
    url(r'^bldgs/name/?$', 'pom.views.make_bldg_names_json'),
    url(r'^events/all/?$', 'pom.views.events_for_all_bldgs'),

    url(r'^pmap/?$', direct_to_template,
        {'template': 'pom/pmap.html'}),

    #Admin
    url(r'^admin/?$', 'django_cas.views.login', kwargs={'next_page': '/djadmin/'}),
    (r'^djadmin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()

