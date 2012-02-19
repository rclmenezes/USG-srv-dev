from dvd.models import *
from django.contrib import admin

class DVDadmin(admin.ModelAdmin):
    fieldsets = [
        (None,                 {'fields': ['name', 'sortname']}),
        ('Rental information', {'fields': ['amountTotal', 'amountLeft', 'timesRented']}), 
        ('IMDB number',        {'fields': ['imdbID']}),
    ]
    
    list_display = ('name', 'amountLeft', 'amountTotal', 'timesRented')
    search_fields = ['name']
    
class RentalAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Basic Info',   {'fields': ['netid', 'dvd']}),
        ('Dates',        {'fields': ['dateRented', 'dateDue', 'dateReturned']}),
    ]

    list_display = ('netid', 'dvd', 'dateRented', 'dateDue', 'dateReturned')

admin.site.register(DVD, DVDadmin)
admin.site.register(Rental, RentalAdmin)
admin.site.register(Notice)