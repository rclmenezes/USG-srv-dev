# -------------------------------------------------------------------#
# models.py                                                          #
# -------------------------------------------------------------------#

from string import ascii_lowercase
from stdimage import StdImageField
from globalsettings import SITE_URL,SITE_EMAIL
from email_msg import *
from django.core.mail import send_mail
from django.db import models
from datetime import date,datetime
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime
from cal.models import Event

# Choices for message settings
MESSAGE_CHOICES = (
    ('M', 'Members'),
    ('O', 'Officers'),
)
COMMENT_CHOICES = (
    ('O', 'Open'),
    ('C', 'Closed'),
)

# choices for email notification (global level)
NOTIFICATION_CHOICES = (
    ('G', 'Use group settings'),
    ('Y', 'Always notify me'),
    ('N', 'Never notify me')
)

# Types of membership
MEM_TYPE_CHOICES = (
    ('M', 'Member'),
    ('S', 'Subscriber'),
    ('O', 'Officer'),
)

# choices for display as a group member
DISPLAY_CHOICES = (
    ('A', 'Any Princeton student'),
    ('S', 'Only members and subscribers of my groups'),
    ('G', 'Only members of my groups'),
)

FILE_CHOICES = (
    ('P', 'Public'),
    ('L', 'Students'),
    ('S', 'Members & Subscribers'),
    ('M', 'Members'),
    ('O', 'Officers')
)

ACTIVE_CHOICES = (
    ('A','Active'),
    ('R','Renewal'),
    ('I','Inactive'),
)


class Category(models.Model):
    category = models.CharField(max_length=3, help_text="3-letter code for category")
    h_name = models.CharField(max_length = 25, help_text="Human-readable category name")

    class Meta:
        db_table = 'groups_categories'
        ordering = ['h_name']
    
    def __unicode__(self):
        return self.h_name

class Student(models.Model):
    netid = models.CharField(max_length=30, primary_key=True, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
#    puid = models.PositiveIntegerField()
    year = models.PositiveIntegerField(blank=True,null=True)
    # Globals for notifications; if None, set at Membership level
    feed_notifications = models.CharField(max_length=1,help_text='Send me an email when one of my groups posts to their feed', choices=NOTIFICATION_CHOICES, default='G')
    mship_notifications = models.CharField(max_length=1,help_text='Send me an email if my membership status changes in a group', choices=NOTIFICATION_CHOICES, default='G')
    message_notifications = models.CharField(max_length=1,help_text='Send me an email when I recieve a message', choices=NOTIFICATION_CHOICES, default='G')
    request_notifications = models.CharField(max_length=1,help_text='Send me an email when students request to become members of a group where I am an officer', choices=NOTIFICATION_CHOICES, default='G')

    def full_name(self):
        return str(self.first_name) + ' ' + str(self.last_name)
    full_name = property(full_name)

    def __unicode__(self):
        return self.netid

    class Meta:
        ordering = ['last_name']
        db_table = 'groups_students'

class Group(models.Model):
    # Profile, required
    name = models.CharField(max_length=100,unique=True)
    description = models.TextField()
    netid = models.CharField(max_length=10)
    # admin
    last_update = models.DateTimeField(default=datetime.now())
    active_status = models.CharField(default='A',max_length=1,choices=ACTIVE_CHOICES)
    date_last_active = models.DateField(blank=True,null=True)
    # Profile, optional
    categories = models.ManyToManyField(Category, blank=True, null=True)
    site = models.URLField(blank=True,null=True)
    email = models.EmailField(blank=True,null=True)
    # Members
    members = models.ManyToManyField(Student, through="Membership")
    show_members = models.BooleanField(default=True, help_text="Allow Princeton students to see the members of this group")
    # Automatically populated, for listing
    sort_letter = models.CharField(max_length=1,blank=True)
    sort_name = models.CharField(max_length=100,blank=True)
    url = models.CharField(max_length=100,blank=True, unique=True)
    # Additional files
    image = StdImageField(upload_to='groups/Images', size=(500,350), thumbnail_size=(100,75,True), blank=True)
    #Other
    ticket = models.CharField(max_length=16, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Populate sort fields
        name = str(self.name).lower()
        if len(name) >= 4 and name[0:4] == 'the ':
            self.sort_letter = name[4]
            self.sort_name = name[4:]
        else:
            self.sort_letter = name[0]
            self.sort_name = name
        ok_list = []
        for l in ascii_lowercase:
            ok_list.append(l)
        ok_list.append('-')
        self.url = self.sort_name.lower().strip().replace(' ','_')
        rm_list = []
        for l in self.url:
            if l not in ok_list:
                rm_list.append(l)
        for l in rm_list:
            self.url = self.url.replace(l,'_')
        self.url = self.url.replace('__','_')
        super(Group, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'groups_groups'
        ordering = ['sort_name']

class GroupReactivationRequest(models.Model):
    group = models.ForeignKey(Group)
    reason = models.CharField(max_length=5000)
    ticket = models.CharField(max_length=16,unique=True)
    supplicant = models.ForeignKey(Student)

    def __unicode__(self):
        return self.group.name

    class Meta:
        db_table = 'groups_reactivation_request'

class GroupFile(models.Model):
    group = models.ForeignKey(Group)
    label = models.CharField(max_length=50, blank=True, null=True,help_text='A description of the file\'s contents; defaults to the name of the file')
    file = models.FileField(max_length=2000,upload_to='groups/Files',help_text='Must be below 2MB')
    permissions = models.CharField(max_length=1, choices=FILE_CHOICES, default='P',help_text='Who can see this file on the group profile')

    class Meta:
        db_table = 'groups_files'
        ordering = ['group','label']

    def __unicode__(self):
        if self.label:
            return self.label
        else:
            return self.file.name

    def save(self, *args, **kwargs):
        if not self.label:
            self.label = self.file.name
        super(GroupFile, self).save(*args, **kwargs)

    
class Link(models.Model):
    label = models.CharField(max_length=50, blank=True, null=True, help_text='A description of this link')
    url = models.URLField()
    group = models.ForeignKey(Group)
    
    class Meta:
        db_table = 'groups_links'
        ordering = ['group', 'label']

    def __unicode__(self):
        if self.label:
            return self.label
        else:
            return self.url

class GroupRequest(models.Model):
    ticket = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)
    netid = models.CharField(max_length=10)
    description = models.TextField()
    site = models.URLField(blank=True,null=True)
    categories = models.ManyToManyField(Category, default='Other')
    #email = models.EmailField(blank=True,null=True)
    president_name = models.CharField(max_length=50)
    president_email = models.CharField(max_length=100)
    supplicant = models.ForeignKey(Student)

    def __unicode__(self):
        return self.name

    def make_group(self):
        try:
            g = Group(name=self.name,description=self.description,site=self.site,netid=self.netid)
            g.save()
            for c in self.categories.all():
                g.categories.add(c)
            g.save()
            m = Membership(student=self.supplicant,group=g,type='O')
            m.save()
            return g
        except:
            try:
                g = Group.objects.get(name=self.name,description=self.description,site=self.site,netid=self.netid)
                g.delete()
                m = Membership.objects.get(student=self.supplicant,group=g,type='O')
                m.delete()
            except:
                pass

    class Meta:
        db_table = 'groups_group_requests'
        ordering = ['name']

class Membership(models.Model):
    student = models.ForeignKey(Student)
    group = models.ForeignKey(Group)
    type = models.CharField(max_length=1, choices=MEM_TYPE_CHOICES, default='S')
    title = models.CharField(max_length=50,blank=True,null=True)
    officer_order = models.PositiveIntegerField(blank=True,null=True, 
                                                help_text='Order in which officers are listed (eg. President = 1, Vice President = 2, ...)')
    has_order = models.BooleanField(default=False)
    display = models.CharField(max_length=1, choices=DISPLAY_CHOICES, default='A', help_text='Who can see my name on this group\'s member list')
    feed_notifications = models.BooleanField(default=True, help_text='Send me emails when this group posts to their feed')
    mship_notifications = models.BooleanField(default=True, help_text='Send me an email when membership status changes for this group')
    message_notifications = models.BooleanField(default=True, help_text='Send me an email when I recieve a message from this group')
    request_notifications = models.BooleanField(default=True, help_text='Send me an email when students request to become members of this group')

    def save(self, *args, **kwargs):
        if self.type == 'O'  and not self.officer_order:
            self.has_order = False
        if not self.type == 'O' and self.title:
            self.title = None
        if not self.type == 'O' and self.officer_order:
            self.officer_order = None
            self.has_order = False
        if self.type == 'O' and self.officer_order:
            self.has_order = True
        super(Membership, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.group) + ': ' + str(self.student)

    class Meta:
        db_table = 'groups_memberships'
        ordering = ['-type','-officer_order','has_order','group']

class MembershipRequest(models.Model):
    student = models.ForeignKey(Student)
    group = models.ForeignKey(Group)
    display = models.CharField(max_length=1, choices=DISPLAY_CHOICES, default='A', help_text='Who can see my name on this group\'s member list')
    feed_notifications = models.BooleanField(default=True, help_text='Send me emails when this group posts to their feed')
    mship_notifications = models.BooleanField(default=True, help_text='Send me an email if my membership status changes for this group')
    message_notifications = models.BooleanField(default=True, help_text='Send me an email when I recieve a message from this group')
    request_notifications = models.BooleanField(default=True, help_text='Send me an email when students request to become members of this group')
    notify_me = models.BooleanField(default=True, help_text="Email me when my request has been processed")

    def make_member(self):
        try:
            m = Membership.objects.get(student=self.student, group=self.group, type='S')
            m.type = 'M'
            m.message_notifications = self.message_notifications
            m.display = self.display
            m.save()
        except:
            m = Membership(student=self.student, group=self.group, display=self.display, feed_notifications=self.feed_notifications, mship_notifications=self.mship_notifications, type='M')
            m.save()
        return True
        

    def __unicode__(self):
        return str(self.group) + ': ' + str(self.student)

    class Meta:
        db_table = 'groups_membership_requests'
        ordering = ['group', 'student']

class Entry(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=100)
    pub_date = models.DateTimeField(default=datetime.now())
    text = models.TextField(blank=True, null=True)
    group = models.ForeignKey(Group)
    event = models.ForeignKey(Event, limit_choices_to={'event_date_time_end__gte':datetime.now()},blank=True, null=True)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return SITE_URL+'feeds/groups/%s/%d' % (self.group.url, self.id)

    class Meta:
        db_table = 'groups_entries'
        ordering = ['-pub_date']

class MessageComment(models.Model):
    pub_date = models.DateTimeField(default=datetime.now())
    text = models.TextField()
    comment_author = models.ForeignKey(Student)
    message = models.ForeignKey('Message')

    def __unicode__(self):
        return self.message+': '+self.pub_date

    class Meta:
        db_table = 'groups_comments'
        ordering = ['-pub_date']

class Message(models.Model):
    title = models.CharField(max_length=100)
    pub_date = models.DateTimeField(default=datetime.now())
    author = models.ForeignKey(Student, related_name='author')
    text = models.TextField(blank=True, null=True)
    group = models.ForeignKey(Group)
    view_permissions = models.CharField(max_length=1, choices=MESSAGE_CHOICES, help_text='Who can view this message',default='M')
    comment_permissions = models.CharField(max_length=1, choices=COMMENT_CHOICES, help_text='Whether members can comment on this message', default='O')
    unread = models.ManyToManyField(Student, related_name='unread')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return SITE_URL+'groups/%s/message/%d' % (self.group.url, self.id)

    class Meta:
        db_table = 'groups_messages'
        ordering = ['-pub_date']
