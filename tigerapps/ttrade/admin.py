from ttrade.models import *
from django.contrib import admin

class ListingAdmin(admin.ModelAdmin):
    #fieldsets = [
        #(None, {'fields': ['title', 'category', 'method', 'listingType']}),
        #("Information", {'fields': ['description', 'user', 'picture', 'price']}),
        #("Other", {'fields': ['flaggers', 'timesViewed', 'expire', 'posted']}),
    #]
    list_display = ('title', 'user', 'category', 'method', 'listingType')
    
class OfferAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['user', 'price', 'additional']})
    ]
    list_display = ('user', 'price', 'additional')
    
admin.site.register(Listing, ListingAdmin)
admin.site.register(Offer, OfferAdmin)