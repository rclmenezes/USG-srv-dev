from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from ptx.offer import *
#from ptx.request import *

admin.autodiscover()

#TODO: We need to create a 404 not found page

urlpatterns = patterns(
    '',

    # The homepage
    (r'^$', 'ptx.homeview.homepage'),

    # login/logout
    (r'^login/?$', 'django_cas.views.login'),
    (r'^logout/?$', 'django_cas.views.logout'),


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
    #(r'^docs/(?P<path>.*)$',
    # 'django.views.static.serve',
    # dict(document_root=settings.DOCS_DIR)),

    # Admin
    url(r'^admin/?$', 'django_cas.views.login', kwargs={'next_page': '/djadmin/'}),
    (r'^djadmin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()

