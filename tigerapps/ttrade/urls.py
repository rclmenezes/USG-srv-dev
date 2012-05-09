from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from rssfeed import NewListings
from ttrade.models import Listing

admin.autodiscover()

feeds = {
'new': NewListings,
}

urlpatterns = patterns('',
    # TigerTrade
    (r'^/?$', 'ttrade.views.home'),
    (r'^create/?$', 'ttrade.views.create'),
    (r'^item/(?P<listingID>\d+)/?$', 'ttrade.views.item'),
    (r'^confirm/?$', 'ttrade.views.confirm'),
    (r'^edit/(?P<listingID>\d+)/?$', 'ttrade.views.edit'),
    (r'^expiration/(?P<listingID>\d+)/?$', 'ttrade.views.expiration'),
    (r'^yourListings/?$', 'ttrade.views.yourListings'),
    (r'^yourOffers/?$', 'ttrade.views.yourOffers'),
    (r'^terms/?$', 'ttrade.views.terms'),
    
    # Login stuff
    (r'^accounts/login/?$', 'django.views.generic.simple.redirect_to', {'url':'/login'}),
    (r'^login/?$', 'ttrade.auth_views.login_choices'),
    (r'^logout/?$', 'ttrade.auth_views.logout_view'),
    (r'^cas/login/?$', 'ttrade.auth_views.cas_login'),
    (r'^cas/logout/?$', 'ttrade.auth_views.cas_logout'),
    (r'^ias/login/?$', 'ttrade.auth_views.ias_login'),
    (r'^ias/logout/?$', 'ttrade.auth_views.ias_logout'),

    # Admin - not upgradable since it doesn't use django_cas
    (r'^admin/', include(admin.site.urls)),
    #url(r'^admin/?$', 'django_cas.views.login', kwargs={'next_page': '/djadmin/'}),
    #(r'^djadmin/', include(admin.site.urls)),
 
    # Feeds
    (r'^feeds/(?P<url>.*)/?$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    (r'^robots\.txt$', direct_to_template,
         {'template': 'robots.txt', 'mimetype': 'text/plain'}),
)

urlpatterns += staticfiles_urlpatterns()

