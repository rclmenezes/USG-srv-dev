################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  urls.py
# Info :  the defined urls for this site
################################################################

from django.conf.urls.defaults import *
from views import *
from views_events import *
from views_users import *
from views_ajax import *
from csvdump import *
from attendee_email import *
from rssfeed import LatestEvents

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

feeds = {
'latest': LatestEvents,
}


urlpatterns = patterns('',

# Front Page and Top Tabs
(r'^$',events),
(r'^today/?$',todays_events),
(r'^week/?$', weeks_events),

(r'^all.ics$', feedAllEvents),
(r'^all/?$', all_events),

(r'^weekend/?$', weekends_events),
(r'^events/?$',events),
(r'(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/?$', events_date),

(r'features/(?P<feature>.*).ics$', feedByFeature),
(r'features/(?P<feature>.*)/?$', filterByFeature),

(r'category/(?P<category>.*).ics$', feedByCategory),
(r'category/(?P<category>.*)$', filterByCategory),

(r'eventsby/(?P<user>.*).ics$', feedByUser),
(r'eventsby/(?P<user>.*)$', filterByUser),

(r'hotevents/?$', showHotEvents),
(r'recentlyadded/?$', showRecentlyAddedEvents),
(r'recentlyviewed/?$', showRecentlyViewedEvents),

(r'feedlanding/?$', feedLanding),



#No Cookie!
(r'^nocookie/?$',nocookie),

# CAS
(r'^login/?$',login),
(r'^logout/?$',logout),

# Event Description Page
(r'^events/(?P<event_id>\d+)/?$',events_description),
(r'^events/(?P<event_id>\d+)/confirm/?$',confirm),
(r'^events/(?P<event_id>\d+)/unconfirm/?$',unconfirm),
(r'^events/invite/?$',invite),
(r'^events/board_message/?$',board_message),
(r'^events/deletebmsg/(?P<bmsg_id>\d+)/?$', delete_bmsg),
(r'^events/reportmsg/(?P<bmsg_id>\d+)/?$', report_bmsg),

# Add Event Page
(r'^events/add/?$',events_add),
(r'^events/add/(?P<event_id>\d+)/?$', events_add_another),

#Forward to campus events list
(r'^events/forwardtocampusevents/?$', events_forwardtocampusevents),

# Manage Event Page  (specific number of numbers?)
(r'^events/manage/(?P<event_ID>\d+)/?$',events_manage_ID),

# Cancel Event
(r'^events/cancel/(?P<event_ID>\d+)/?$', events_cancel),
(r'^events/cancel_confirm/(?P<event_ID>\d+)/?$', events_cancel_confirm),

# Delete Event
(r'^events/delete/(?P<event_ID>\d+)/?$', events_delete),
(r'^events/delete_confirm/(?P<event_ID>\d+)/?$', events_delete_confirm),

# Search Results
(r'^search/?$',events_search),

# Manage Profile
(r'^user/?$',user_profile),

# My Events
(r'^user/events/?$',user_upcoming_events),

# My Past Events
(r'^user/oldevents/?$', user_past_events),

# My Managed Events
(r'^user/eventadmin/?$', user_admin_events),

# Invitations
(r'^user/invitations/?$',user_invitations),
(r'^user/invitations/(?P<invite_id>\d+)/(?P<action>accept|decline)/?$',invite_response),
(r'^bulkinvite/(?P<event_id>\d+)-(?P<sender_id>\d+)-(?P<response>a|d|p)/?$',bulk_invite_response),

# Set Personal Alerts
(r'^user/alerts/?$',user_alerts),
(r'^user/messages/?$',user_messages),
(r'^user/messages/hover.html$',user_messages_hover),

#Feeds of type ics
(r'category/(?P<category>.*).ics$', feedByCategory),
#(r'^feeds/category/(?P<category>\d+).ics$', feedCategory),

# iCal   
(r'^ical/(?P<event_id>\d+)/?$', ical),
(r'^(?P<category>.*)/subscription.ics$', icalFeed),
(r'^subscribe/(?P<category>.*).ics$', subscribe),
(r'^mycal/(?P<id>\d+)/(?P<netid>.*).ics$', feedMyEvents),
(r'^follow/(?P<netid>.*).ics$', followCalendar),

# Send emails to attendees
(r'^events/(?P<event_id>\d+)/sendmsg/?$', form_email_attendees),
(r'^events/(?P<event_id>\d+)/msgsent/?$', email_attendees),

#Get attendee list
(r'^events/(?P<event_id>\d+)/attendees.csv$', downloadAttendeeList),

# Send custom invitations
(r'^events/(?P<event_id>\d+)/custominvite/?$', custom_invite_message),
(r'^events/(?P<event_id>\d+)/custominvitesent/?$', custom_invite_message_sent),

#QR Code
(r'^events/(?P<event_id>\d+)/qr/?$', showQR),

# Ajax goodness
(r'^ajax/netidlookup/?$',netidlookup),
(r'^ajax/allguests/?$',allguests),

# Feed
(r'^feeds/(?P<url>.*)/?$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),

(r'^adminfun/?$',activityFeed),
(r'^lookup/?$',userlookup),


# XML Feed
(r'^xml/?$', xml_feed),

# Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
# to INSTALLED_APPS to enable admin documentation:
# (r'^admin/doc/', include('django.contrib.admindocs.urls')),

# Uncomment the next line to enable the admin:
(r'^admin/', include(admin.site.urls)),
)
