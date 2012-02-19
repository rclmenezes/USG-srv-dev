################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  admin.py
# Info :  tell the Django admin system which models to make
#		  available in the backend
################################################################

from models import *
from django.contrib import admin

class CalUserAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,                 {'fields': ['user_netid', 'user_email', 'user_firstname', 'user_lastname']}),
        ('Rental information', {'fields': ['user_pustatus', 'user_dept', 'user_last_login', 'user_recently_viewed_events', 'user_privacy_enabled', 'user_reminders_requested', 'user_notify_invitation']}), 
    ]
    search_fields = ['user_netid']
    
class EventClusterAdmin(admin.ModelAdmin):
    search_fields = ['cluster_title']

admin.site.register(Event)
admin.site.register(EventCluster, EventClusterAdmin)
admin.site.register(CalUser, CalUserAdmin)
admin.site.register(BoardMessage)
admin.site.register(RSVP)
admin.site.register(EventFeature)
admin.site.register(EventCategory)
admin.site.register(UserMessage)
admin.site.register(VisitorMessage)
admin.site.register(View)
admin.site.register(WebcalSubscription)
