from ttrade.models import *
from django.contrib import admin

class ListingAdmin(admin.ModelAdmin):
    #fieldsets = [
        #(None, {'fields': ['title', 'category', 'method', 'listingType']}),
        #("Information", {'fields': ['description', 'user', 'picture', 'price']}),
        #("Other", {'fields': ['flaggers', 'timesViewed', 'expire', 'posted']}),
    #]
    list_display = ('user', 'title', 'category', 'method', 'listingType', 'expire')
    search_fields = ['title', 'description', 'user__username']
    
class OfferAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['user', 'price', 'additional']})
    ]
    list_display = ('user', 'price', 'additional')
    search_fields = ['user__username']
    
admin.site.register(Listing, ListingAdmin)
admin.site.register(Offer, OfferAdmin)
