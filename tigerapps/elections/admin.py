from elections.models import *
from django.contrib import admin

class CandidateAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,          {'fields': ['netid', 'name', 'year', 'statement']}),
        ('Office',      {'fields': ['office', 'election']}), 
        ('Image',       {'fields': ['headshot']}),
    ]
    
    list_display = ('name', 'netid', 'office')
    search_fields = ['name', 'netid']
    
class OfficeAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,          {'fields': ['name']}),
        ('Eligibility', {'fields': ['freshman_eligible', 'sophomore_eligible', 'junior_eligible']}), 
        ('Vote',        {'fields': ['freshman_vote', 'sophomore_vote', 'junior_vote', 'senior_vote']}),
    ]

    search_fields = ['name']
    
class ElectionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,                {'fields': ['name', 'offices']}),
        ('Dates',             {'fields': ['deadline', 'start', 'end']}),
    ]

    search_fields = ['name']

admin.site.register(Office, OfficeAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Election, ElectionAdmin)