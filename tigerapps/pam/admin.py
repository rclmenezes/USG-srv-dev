from models import *
from django.contrib import admin

class SocUserAdmin(admin.ModelAdmin):
    list_display = ('netid', 'firstname', 'lastname', 'officer_at', 'is_president')
    fieldsets = [
        (None, {'fields': ['netid', 'firstname', 'lastname', 'pustatus', 'puclassyear', 'officer_at', 'is_president']})
    ]
    search_fields = ['netid', 'firstname', 'lastname']

class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    fieldsets = [
        (None, {'fields': ['name', 'nickname', 'slug', 'about', 'left_offset', 'top_offset', 'width', 'picture', 'active', 'active_selected', 'inactive', 'inactive_selected']})
    ]
    
class EventAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['club', 'title', 'entry', 'entry_description', 'description', 'time_start', 'time_end', 'poster']})
    ]
    list_display = ('event_id', 'club', 'title', 'time_start', 'entry')
    
admin.site.register(SocUser, SocUserAdmin)
admin.site.register(Club, ClubAdmin)
admin.site.register(Event, EventAdmin)