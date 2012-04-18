from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^/?$', 'dvd.views.home', name='home'),
    url(r'^checkout/?$', 'dvd.views.checkout', name='checkout'),
    url(r'^checkin/?$', 'dvd.views.checkin_choices', name='checkin_choices'), # Choices
    url(r'^checkin/user/?$', 'dvd.views.checkin_user', name='checkin_user'), # By netid
    url(r'^checkin/dvd/?$', 'dvd.views.checkin_dvd', name='checkin_dvd'), # By netid
    url(r'^checkin/dvdlist/?$', 'dvd.views.checkin_dvdlist', name='checkin_dvdlist'), # By DVD List
    url(r'^checkout/user/?$', 'dvd.views.checkout_user', name='checkout_user'), 
    url(r'^checkout/dvd/?$', 'dvd.views.checkout_dvd', name='checkout_dvd'),
    url(r'^admin/?$', 'dvd.views.admin', name='admin'),
    url(r'^ambiguous/?$', 'dvd.views.ambiguous', name='ambiguous'),
    url(r'^adduser/?$', 'dvd.views.adduser', name='adduser'),
    url(r'^adddvd/?$', 'dvd.views.adddvd', name='adddvd'),
    url(r'^outstanding/?$', 'dvd.views.outstanding', name='outstanding'),
    url(r'^edit/?$', 'dvd.views.edit', name='edit'),
    url(r'^edit/(?P<dvd_id>\d+)/?$', 'dvd.views.editdvd', name='editdvd'),
    url(r'^notify/(?P<dvd_id>\d+)/?$', 'dvd.views.notify', name='notify'),
    url(r'^delete/(?P<dvd_id>\d+)/?$', 'dvd.views.delete', name='delete'),
    (r'^login/?$', 'django_cas.views.login'),
    (r'^logout/?$', 'django_cas.views.logout'),
    # url(r'^combo/', include('combo.foo.urls')),

    # Admin
    url(r'^admin/?$', 'django_cas.views.login', kwargs={'next_page': '/djadmin/'}),
    (r'^djadmin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()

