################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  rssfeed.py
# Info :  helps generate the rss feed for the site
################################################################

from django.contrib.syndication.feeds import Feed
from models import *
from datetime import datetime
from globalsettings import our_site

class LatestEvents(Feed):
    title = "Princeton Events Calendar - Hosted by the Princeton USG"
    link = "%sevents" % our_site
    description = "Upcoming events listed on the Princeton Events Calendar, online at %s." % our_site

    def items(self):
        return Event.objects.filter(event_date_time_end__gte=datetime.now()).order_by('event_date_time_start')[:20]

    def item_pubdate(self, item):
        return item.event_date_time_start	
    
    def item_link(self, item):
    	return '%sevents/%s' % (our_site, item.pk)
