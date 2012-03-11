from django.conf.urls.defaults import *
from django.conf import settings

from ptx.offer import *
#from ptx.request import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

#TODO: We need to create a 404 not found page

urlpatterns = patterns(
    '',

    # The homepage
    (r'^$', 'ptx.homeview.homepage'),

    # login/logout
    (r'^login$', 'ptx.ptxlogin.ptxlogin'),
    (r'^logout$', 'ptx.ptxlogin.ptxlogout'),

    # Move these URLS to ptx folder sometime
    (r'^browse$', 'ptx.views.classlistings'),
    (r'^browse/(?P<isbn>([0-9])+)$', 'ptx.views.browse_isbn'),
    (r'^browse/(?P<dept>\D+)(?P<num>\d+)$',
     'ptx.views.browse_class'),
    (r'^search$', 'ptx.views.search'),

    # Buying a book
    (r'^buy/confirm$', 'ptx.buy.confirm'),
    (r'^buy$', 'ptx.buy.buy'),

    # user profile  pages
    (r'^account$', 'ptx.profile.myaccount'),
    (r'^profile$', 'ptx.profile.profile'),

    # Offer pages
    (r'^offer$', 'ptx.offer.offer'),
    (r'^offer_(?P<step>[0-9])_(?P<ticket>([a-z0-9])+)$',
     'ptx.offer.process'),
    (r'^offer/thankyou$', 'ptx.thankyou.offer'),

    # Change an offer
    (r'^editoffer/(?P<offer_id>\d+)$', 'ptx.editoffer.editoffer'),

    # Wishlist
    (r'^wishlist/?$', 'ptx.wishlist.wishlist'),

    # Help
    (r'^help$', 'ptx.help.help'),

    # Request pages
    (r'^request$', 'ptx.request.request'),
    (r'^request/thankyou$', 'ptx.thankyou.request'),
    (r'^request_(?P<step>[0-9])_(?P<ticket>([a-z0-9])+)$',
     'ptx.request.process'),

    # server css files
    (r'^site_media/css/(?P<path>.*)$',
     'django.views.static.serve',
     dict(document_root=settings.STATIC_DOC_ROOT)),
    (r'^book_cache/(?P<path>.*)$',
     'django.views.static.serve',
     dict(document_root=settings.BOOK_CACHE_DIR)),
    (r'^docs/(?P<path>.*)$',
     'django.views.static.serve',
     dict(document_root=settings.DOCS_DIR)),
    (r'^favicon\.ico$',
     'django.views.generic.simple.redirect_to',
     dict(url='/site_media/css/favicon.ico')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment for admin.
    # (r'^admin/(.*)', admin.site.root),
)
