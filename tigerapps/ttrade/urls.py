from django.conf.urls.defaults import *
from rssfeed import LatestListings
from django.contrib import admin
admin.autodiscover()

feeds = {
'latest': LatestListings,
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
    (r'^terms/?$', 'ttrade.views.terms'),
    
    # Login stuff
    (r'^accounts/login/?$', 'django.views.generic.simple.redirect_to', {'url':'/login'}),
    (r'^login/?$', 'ttrade.auth_views.login_choices'),
    (r'^logout/?$', 'ttrade.auth_views.logout_view'),
    (r'^cas/login/?$', 'ttrade.auth_views.cas_login'),
    (r'^cas/logout/?$', 'ttrade.auth_views.cas_logout'),
    (r'^ias/login/?$', 'ttrade.auth_views.ias_login'),
    (r'^ias/logout/?$', 'ttrade.auth_views.ias_logout'),

    # Admin
    (r'^admin/', include(admin.site.urls)),
    
    # Feeds
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
)
