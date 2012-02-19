from django.contrib.syndication.feeds import Feed, FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from models import *
from datetime import datetime
from globalsettings import SITE_URL

class LatestEntries(Feed):
    title = "Princeton Student Groups feed"
    link = SITE_URL
    description = "News for Princeton student groups."

    def items(self):
        return Entry.objects.all()

class GroupFeed(Feed):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Group.objects.get(url__exact=bits[0])

    def title(self, obj):
        return "Princeton Student Groups: %s Feed" % obj.name

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return SITE_URL+'groups/%s/'%obj.url

    def description(self, obj):
        return 'News for %s' % obj.name

    def author_name(self, obj):
        return obj.name

    def author_link(self, obj):
        return SITE_URL+'groups/%s/'%obj.url

    def item_pubdate(self, obj):
        return obj.pub_date

    def item_link(self, obj):
        return SITE_URL+"groups/%s/post/%d/"%(obj.group.url,obj.id)

    def item_author_name(self, obj):
        return obj.group.name

    def item_author_link(self, obj):
        return SITE_URL+'groups/%s/'%obj.group.url

    def items(self, obj):
        return Entry.objects.filter(group__url__exact=obj.url)

class StudentFeed(Feed):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Student.objects.get(netid__exact=bits[0])

    def title(self, obj):
        return "Princeton Student Groups: %s %s's Feed" % (obj.first_name,obj.last_name)

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return SITE_URL

    def description(self, obj):
        return 'News for %s %s' % (obj.first_name,obj.last_name)

    def item_pubdate(self, obj):
        return obj.pub_date

    def item_link(self, obj):
        return SITE_URL+"groups/%s/post/%d/"%(obj.group.url,obj.id)

    def item_author_name(self, obj):
        return obj.group.name

    def item_author_link(self, obj):
        return SITE_URL+'groups/%s/'%obj.group.url

    def items(self, obj):
        groups = Membership.objects.filter(student__netid__exact=obj.netid).values('group')
        return Entry.objects.filter(group__in=groups)
