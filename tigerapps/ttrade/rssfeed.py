from django.contrib.syndication.feeds import Feed
from models import Listing
from datetime import datetime
from django.conf import settings

class NewListings(Feed):
    title = "Princeton TigerTrade Listings - Hosted by Princeton USG"
    link = "http://ttrade.tigerapps.org/events"
    description = "Listings at TigerTrade, online at http://%sttrade.tigerapps.org." % settings.CURRENT_HOST_PREFIX

    def items(self):
        return Listing.objects.filter(expire__gte=datetime.now()).order_by('expire').reverse()[:20]

    def item_pubdate(self, item):
        return item.posted	
    
    def item_link(self, item):
    	return 'http://ttrade.tigerapps.org/item/%s' % item.listingID
