from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
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
    (r'^robots\.txt$', direct_to_template,
         {'template': 'robots.txt', 'mimetype': 'text/plain'}),
    # url(r'^combo/', include('combo.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^djangoadmin/', include(admin.site.urls)),
)
