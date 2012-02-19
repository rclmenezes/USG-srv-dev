from django.conf.urls.defaults import *
from models import *
from rss import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from adminsites import groupsAdmin
admin.autodiscover()

feeds = {
    'latest': LatestEntries,
    'groups':GroupFeed,
    'students':StudentFeed,
}

urlpatterns = patterns('',

                       # fake login for testing
                       (r'^test/?$', 'groups.test.login'),
                       
                       # browsing groups
                       (r'^groups/?$', 'groups.groups.list'),
                       (r'^category/(?P<category>\w+)/?$', 'groups.groups.category'),

                       # group profile, membership options
                       (r'^groups/(?P<group>\w+)/?$', 'groups.groups.profile'),
                       (r'^groups/(?P<group>\w+)/request/?$', 'groups.groups.request'),
                       (r'^groups/(?P<group>\w+)/withdraw/?$', 'groups.groups.withdraw'),
                       (r'^groups/(?P<group>\w+)/subscribe/?$', 'groups.groups.subscribe'),
                       (r'^groups/(?P<group>\w+)/settings/?$', 'groups.mship.settings'),
                       (r'^groups/(?P<group>\w+)/memberslist/?$', 'groups.groups.member_list'),
                       
                       # leadership section
                       (r'^leadership/?$', 'groups.leadership.leadership'),

                       # search
                       (r'^search/?$', 'groups.groups.search'),
                       
                       # Editing groups
                       (r'^groups/(?P<group>\w+)/edit/?$', 'groups.edit.edit_profile'),
                       (r'^groups/(?P<group>\w+)/approve/?$', 'groups.edit.approve_members'),
                       (r'^groups/(?P<group>\w+)/members/?$', 'groups.edit.edit_members'),
                       (r'^groups/(?P<group>\w+)/files/?$', 'groups.edit.files'),

                       # group renewal, deactivation, reactivation
                       (r'^groups/(?P<group>\w+)/reactivate/?$', 'groups.activity.reactivate'),
                       (r'^groups/(?P<group>\w+)/renew/?$', 'groups.activity.renew'),
                       (r'^reactivate/(?P<ticket>\w+)/?$', 'groups.activity.reactivate_process'),

                       # feed
                       (r'^groups/(?P<group>\w+)/feed/?$', 'groups.feed.all_entries'),
                       (r'^groups/(?P<group>\w+)/post/?$', 'groups.feed.post'),
                       (r'^groups/(?P<group>\w+)/post/(?P<entry>\w+)/?$', 'groups.feed.edit_post'),
                       (r'^groups/(?P<group>\w+)/post/(?P<entry>\w+)/delete/?$', 'groups.feed.delete_post'),

                       # message board
                       (r'^groups/(?P<group>\w+)/sendmessage/?$', 'groups.feed.send_message'),
                       (r'^groups/(?P<group>\w+)/sendmessage/(?P<message>\w+)/?$', 'groups.feed.edit_message'),
                       (r'^groups/(?P<group>\w+)/messages/?$', 'groups.feed.group_messages'),
                       (r'^groups/(?P<group>\w+)/messages/(?P<message>\w+)/?$', 'groups.feed.read_group_message'),
                       (r'^groups/(?P<group>\w+)/messages/(?P<message>\w+)/read_comments/?$', 'groups.feed.read_comments'),
                       (r'^groups/(?P<group>\w+)/messages/(?P<message>\w+)/delete/?$', 'groups.feed.delete_group_message'),
                       (r'^groups/(?P<group>\w+)/messages/(?P<message>\w+)/comment/?$', 'groups.feed.comment_group_message'),
                       (r'^groups/(?P<group>\w+)/messages/(?P<message>\w+)/comment/(?P<comment>\w+)/delete/?$', 'groups.feed.delete_comment'),

                       # Account
                       (r'^account/groups/?$', 'groups.account.groups'),
                       (r'^account/manage/?$', 'groups.account.manage'),
                       (r'^account/register/?$', 'groups.account.register_group'),
                       (r'^process/(?P<ticket>\w+)/?$', 'groups.account.process'),
                       
                       # help
                       (r'^help/?$', 'groups.help.help'), 
                       (r'^help/follow/?$', 'groups.help.help_follow'),
                       (r'^help/officer/?$', 'groups.help.help_officer'),
                       (r'^help/account/?$', 'groups.help.help_account'), 
                       
                       # CAS
                       (r'^accounts/login/?$', 'django_cas.views.login'),
                       (r'^logout/?$', 'groups.views.logout'),
                       (r'^accounts/logout/?$', 'django_cas.views.logout'),

                       # Downloads
                       (r'^media/(?P<path>.*)$', 'django.views.static.serve',
                        {'document_root': '/home/atrippe/Student_Groups/media/groups'}),

                       # RSS Feeds
                       (r'^feeds/(?P<url>.*)/?$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
                     
                       # Uncomment the next line to enable the admin:
                        (r'^admin/?', include(groupsAdmin.urls)),
                       (r'^$', 'groups.views.index'),
#                       (r'^', 'groups.views.redirect_index'),
)
