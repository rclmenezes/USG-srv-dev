from django.db import models
from stdimage import StdImageField

class SocUser(models.Model):
    netid = models.CharField("netid", max_length=8)
    firstname = models.CharField('First Name', max_length=45, null=True, blank=True) # givenName
    lastname = models.CharField('Last Name', max_length=45, null=True, blank=True) # sn
    pustatus = models.CharField(max_length=20, null=True, blank=True) # undergraduate or graduate
    puclassyear = models.IntegerField('Class Year', null=True, blank=True) # puclassyear
    officer_at = models.ForeignKey('Club', null=True, blank=True)
    is_president = models.BooleanField(default=False)

class Club(models.Model):
    club_id = models.AutoField(primary_key=True)
    name = models.CharField("Name", max_length=30)
    nickname = models.CharField("Nickname", help_text="Used for default names", max_length=30, null=True, blank=True)
    slug = models.CharField("Slug", help_text="Used for URLs", max_length=30, unique=True)
    about = models.TextField("About", null=True, blank=True)
    left_offset = models.IntegerField("Left offset")
    top_offset = models.IntegerField("Top offset")
    width = models.IntegerField("Width")
    picture = StdImageField('Club picture', upload_to='social/images/picture', size=(300, 196), blank=True, null=True)
    active = StdImageField('Active', upload_to='social/images/active', blank=True, null=True)
    active_selected = StdImageField('Active Selected', upload_to='social/images/active_selected', blank=True, null=True)
    inactive = StdImageField('Inactive', upload_to='social/images/inactive', blank=True, null=True)
    inactive_selected = StdImageField('Inactive Selected', upload_to='social/images/inactive_selected', blank=True, null=True)

    def __unicode__(self):
        return self.name
        
ACCESS_CHOICES = (
    (u'Pu', u'PUID'),
    (u'Pa', u'Pass'),
    (u'Me', u'Members only'),
    (u'Mp', u'Members + '),
    (u'Gu', u'Guestlist'),
    (u'Cu', u'Custom'),
)

class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    club = models.ForeignKey('Club')
    entry = models.CharField('Entry', max_length=2, choices=ACCESS_CHOICES)
    entry_description = models.CharField("Entry Description", help_text="Useful for describing passes or members +.", max_length=40, null=True, blank=True)
    title = models.CharField("Title", help_text="Default is clubname + weekday", max_length=40, null=True, blank=True)
    description = models.TextField("Description", null=True, blank=True)
    poster = StdImageField('Event Poster (optional)', upload_to='social/images/', size=(400,600), thumbnail_size=(250, 375), blank=True, null=True)
    time_start = models.DateTimeField('Start datetime')
    time_end = models.DateTimeField('End datetime')
    
    def __unicode__(self):
        if self.title:
            return self.title
        return self.club.name + " " + self.time_start.strftime("%A")