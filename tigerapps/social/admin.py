from social.models import *
from django.contrib import admin

class SocUserAdmin(admin.ModelAdmin):
    list_display = ('netid', 'firstname', 'lastname')
    fieldsets = [
        (None, {'fields': ['netid', 'firstname', 'lastname', 'pustatus', 'puclassyear']})
    ]

class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    fieldsets = [
        (None, {'fields': ['name', 'nickname', 'slug', 'about', 'left_offset', 'top_offset', 'width', 'picture', 'active', 'active_selected', 'inactive', 'inactive_selected']})
    ]
    
class EventAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['club', 'title', 'entry', 'entry_description', 'description', 'time_start', 'time_end', 'poster']})
    ]
    list_display = ('club', 'title', 'time_start', 'entry')
    
admin.site.register(SocUser, SocUserAdmin)
admin.site.register(Club, ClubAdmin)
admin.site.register(Event, EventAdmin)