<<<<<<< HEAD
import tigeralbum.settings as settings
=======
import album.settings as settings
>>>>>>> 1994cf8d56d0192da28cf65baa61dffc0640b457
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
<<<<<<< HEAD
    (r'^$', 'tigeralbum.main.views.main'),
    (r'^help/$', direct_to_template, {'template': 'faq.html' }),
    (r'^contact/$', 'tigeralbum.main.views.contact'),

    # Submission.
    (r'^submit/$', 'tigeralbum.main.views.submit'),
    (r'^submit/(?P<id>\d+)/locate$', 'tigeralbum.main.views.submit_update'),

    # Search.
    (r'^search/$', 'tigeralbum.main.views.search'),

    # API calls made by JavaScript.
    (r'^api/photos.json$', 'tigeralbum.main.api.photos'),
    (r'^api/details.json$', 'tigeralbum.main.api.details'),
    (r'^api/submit_comment.json$', 'tigeralbum.main.api.submit_comment'),
    (r'^api/like.json$', 'tigeralbum.main.api.like'),
    (r'^api/report_image.json$', 'tigeralbum.main.api.report_image'),
    (r'^api/report_comment.json$', 'tigeralbum.main.api.report_comment'),
    (r'^api/comments.html$', 'tigeralbum.main.api.comments'),

    # Moderation.
    (r'^login/$', 'tigeralbum.main.views.mod_login'),
    (r'^mod/$', 'tigeralbum.main.views.mod_index'),
    (r'^mod/photo_approve$', 'tigeralbum.main.views.mod_photo_approve'),
    (r'^mod/photo_approve_ip$', 'tigeralbum.main.views.mod_photo_approve_ip'),
    (r'^mod/photo_review$', 'tigeralbum.main.views.mod_photo_review'),
    (r'^mod/comment_review$', 'tigeralbum.main.views.mod_comment_review'),
    (r'^mod/logout$', 'tigeralbum.main.views.mod_logout'),
    (r'^mod/change_password$', 'tigeralbum.main.views.change_password'),
    (r'^mod/mod_list$', 'tigeralbum.main.views.mod_list'),
=======
    (r'^$', 'album.main.views.main'),
    (r'^help/$', direct_to_template, {'template': 'faq.html' }),
    (r'^contact/$', 'album.main.views.contact'),

    # Submission.
    (r'^submit/$', 'album.main.views.submit'),
    (r'^submit/(?P<id>\d+)/locate$', 'album.main.views.submit_update'),

    # Search.
    (r'^search/$', 'album.main.views.search'),

    # API calls made by JavaScript.
    (r'^api/photos.json$', 'album.main.api.photos'),
    (r'^api/details.json$', 'album.main.api.details'),
    (r'^api/submit_comment.json$', 'album.main.api.submit_comment'),
    (r'^api/like.json$', 'album.main.api.like'),
    (r'^api/report_image.json$', 'album.main.api.report_image'),
    (r'^api/report_comment.json$', 'album.main.api.report_comment'),
    (r'^api/comments.html$', 'album.main.api.comments'),

    # Moderation.
    (r'^login/$', 'album.main.views.mod_login'),
    (r'^mod/$', 'album.main.views.mod_index'),
    (r'^mod/photo_approve$', 'album.main.views.mod_photo_approve'),
    (r'^mod/photo_approve_ip$', 'album.main.views.mod_photo_approve_ip'),
    (r'^mod/photo_review$', 'album.main.views.mod_photo_review'),
    (r'^mod/comment_review$', 'album.main.views.mod_comment_review'),
    (r'^mod/logout$', 'album.main.views.mod_logout'),
    (r'^mod/change_password$', 'album.main.views.change_password'),
    (r'^mod/mod_list$', 'album.main.views.mod_list'),
>>>>>>> 1994cf8d56d0192da28cf65baa61dffc0640b457
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^photos/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT + '/photos',
        }),
   )
