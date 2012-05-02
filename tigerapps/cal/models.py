################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  models.py
# Info :  all of our database models
################################################################

from django.db import models
from datetime import datetime, date, timedelta
from stdimage import StdImageField
from globalsettings import SITE_ADMINS, dtdeleteflag, our_site

BLDG_CODE = (
    ('AL099', '99 Alexander (Forbes College)'),
    ('ALEXH', 'Alexander Hall'),
    ('ARCHB', 'Architecture Building'),
    ('ARCHL', 'Architectural Laboratory'),
    ('ARTMU', 'Art Museum'),
    ('BENDC', 'Bendheim Center'),
    ('BENDH', 'Bendheim Hall'),
    ('BERLT', 'Berlind Theatre'),
    ('BLAIR', 'Blair Hall'),
    ('BOBSH', 'Bobst Hall'),
    ('BOWEN', 'Bowen Hall'),
    ('BR171', 'Broadmead, 171'),
    ('BURRH', 'Aaron Burr Hall'),
    ('C1879', 'Class of 1879 Hall'),
    ('C1915', '1915 Hall'),
    ('CARRS', 'Career Services'),
    ('CCAMP', 'Campus Club'),
    ('CCAPA', 'Cap and Gown Club'),
    ('CCHAR', 'Charter Club'),
    ('CCLOI', 'Cloister Club'),
    ('CCOLO', 'Colonial Club'),
    ('CCOTT', 'Cottage Club'),
    ('CENJL', 'Center for Jewish Life'),
    ('CFCTR', 'Carl A. Fields Center'),
    ('CHANC', 'Chancellor Green'),
    ('CLIOH', 'Clio Hall'),
    ('COMPU', 'Computer Science Building'),
    ('CORWH', 'Corwin Hall'),
    ('CQUAD', 'Quadrangle Club'),
    ('CTERR', 'Terrace Club'),
    ('CTOWE', 'Tower Club'),
    ('DICKH', 'Dickinson Hall'),
    #('DILCE', 'Dillon Court East'),
    #('DILCW', 'Dillon Court West'),
    ('DILLG', 'Dillon Gymnasium'),
    ('ELPLE', 'Elementary Particles Lab East'),
    ('ENOHA', 'Eno Hall'),
    ('EPYNE', 'East Pyne Building'),
    ('EQUAA', 'Engineering Quad - A Wing'),
    ('EQUAB', 'Engineering Quad - B Wing'),
    ('EQUAC', 'Engineering Quad - C Wing'),
    ('EQUAD', 'Engineering Quad - D Wing'),
    ('EQUAE', 'Engineering Quad - E Wing'),
    ('EQUAF', 'Engineering Quad - F Wing'),
    ('EQUAG', 'Engineering Quad - G Wing'),
    ('EQUAJ', 'Engineering Quad - J Wing'),
    ('FINEH', 'Fine Hall'),
    ('FIRES', 'Firestone Library'),
    ('FISHH', 'Fisher Hall'),
    ('FITZO', 'FitzRandolph Observatory'),
    ('FORBC', 'Forbes College Main'),
    ('FORRT', 'Forrestal Campus'),
    ('FRICK', 'Frick Chemistry Laboratory'),
    ('FRIEN', 'Friend Center'),
    ('FRIST', 'Frist Campus Center'),
    ('GREEN', 'Green Hall'),
    ('GUYOT', 'Guyot Hall'),
    ('HAMIL', 'Hamilton Hall'),
    ('HARGH', 'Whitman College Hargadon Hall'),
    ('HENHO', 'Henry House'),
    ('HOLDE', 'Holder Hall'),
    ('HOYTL', 'Hoyt Chemical Laboratory'),
    ('ICAHN', 'Carl Icahn Laboratory'),
    ('IVY05', 'Ivy Lane, 5'),
    ('JADWH', 'Jadwin Hall'),
    ('JOLIN', 'Joline Hall'),
    ('JONES', 'Jones Hall'),
    ('LEWLI', 'Lewis Library'),
    ('MADIH', 'Madison Hall'),
    ('MARXH', 'Marx Hall'),
    ('MCCKH', 'McCormick Hall'),
    ('MCCOH', 'McCosh Hall'),
    ('MCDON', 'James S. McDonnell Hall'),
    ('MOFFH', 'Moffett Laboratory'),
    ('MUDDL', 'Mudd Manuscript Laboratory'),
    ('NA185', 'Nassau Street, 185'),
    ('NA201', 'Nassau Street, 201'),
    ('ORFES', 'Sherrerd Hall'),
    #('PAL01', 'Palmer Square'),
    ('PEYTH', 'Peyton Hall'),
    ('PRO58', '58 Prospect'),
    ('ROBEH', 'Robertson Hall'),
    ('ROCKL', 'Rock Magnetism Laboratory'),
    ('SCCAH', 'Scheide Caldwell House'),
    ('SCHUL', 'Schultz Laboratory'),
    ('STANH', 'Stanhope'),
    ('STH91', 'Prospect Avenue, 91'),
    ('THOML', 'Thomas Laboratory'),
    ('VONNH', 'Von Neumann Hall'),
    ('WALLB', 'Wallace Social Science'),
    ('WHIGH', 'Whig Hall'),
    ('WIL41', 'William Street, 41'),
    ('WILCH', 'Wilcox Hall'),
    ('WOOLC', 'Woolworth Music Center'),
    ('WUHAL', 'Wu Hall'),
)

VALID_DATETIMES = [
'%Y-%m-%d',              # '2006-10-25'
'%m/%d/%Y',              # '10/25/2006'
'%m/%d/%y',              # '10/25/06'
'%Y-%m-%d %H:%M:%S',     # '2006-10-25 14:30:59'
'%Y-%m-%d %H:%M',        # '2006-10-25 14:30'
'%m/%d/%Y %H:%M:%S',     # '10/25/2006 14:30:59'
'%m/%d/%Y %H:%M',        # '10/25/2006 14:30'
'%m/%d/%y %H:%M:%S',     # '10/25/06 14:30:59'
'%m/%d/%y %H:%M',        # '10/25/06 14:30'

'%Y-%m-%d %I:%M:%S%p',     # '2006-10-25 02:30:59PM
'%Y-%m-%d %I:%M%p',        # '2006-10-25 02:30PM
'%m/%d/%Y %I:%M:%S%p',     # '10/25/2006 02:30:59PM
'%m/%d/%Y %I:%M%p',        # '10/25/2006 02:30PM
'%m/%d/%y %I:%M:%S%p',     # '10/25/06 02:30:59PM
'%m/%d/%y %I:%M%p',        # '10/25/06 02:30PM

'%Y-%m-%d %l:%M:%S%p',     # '2006-10-25 2:30:59PM
'%Y-%m-%d %l:%M%p',        # '2006-10-25 2:30PM
'%m/%d/%Y %l:%M:%S%p',     # '10/25/2006 2:30:59PM
'%m/%d/%Y %l:%M%p',        # '10/25/2006 2:30PM
'%m/%d/%y %l:%M:%S%p',     # '10/25/06 2:30:59PM
'%m/%d/%y %l:%M%p',        # '10/25/06 2:30PM
]



class CalUser(models.Model):
	#Netid of the user (guaranteed to exist)
	user_netid = models.CharField(max_length=8)
	
	#User's email address (user-specifiable)
	user_email = models.CharField('Email Address', max_length=30)#NEW
	
	#User's first name (prepopulated, modifiable)
	user_firstname = models.CharField('First Name', max_length=45)
	
	#User's first name (prepopulated, modifiable)
	user_lastname = models.CharField('Last Name', max_length=45)
	
	#User's retrieved pustatus -- 'u12' for example for class of 2012
	user_pustatus = models.CharField(max_length=3)
	
	#User's retrieved department -- informational only
	user_dept = models.CharField(max_length=60)#NEW
	
	#Date and time of user's last login <TODO>
	user_last_login = models.DateTimeField(blank=True, null=True)
	
	#Events the user recently viewed <TODO>
	user_recently_viewed_events = models.ManyToManyField('Event', blank=True)
	
	#Whether this user's name will show up as someone coming to an event
	user_privacy_enabled = models.BooleanField('Anonymous Attendance',help_text='Prevent your name from appearing in the list of attendees.')
	
	#Whether this user will get emailed reminders about upcoming events
	user_reminders_requested = models.BooleanField('Get Reminder Emails',help_text='Receive a helpful reminder email the morning before an event you are attending.')
	
	#Whether this user will get emailed when an invitation is received
	user_notify_invitation = models.BooleanField('Emails upon Invitation',help_text='Receive an email letting you know when someone has sent you an invitation.')
	
	def __unicode__(self):
	  return self.user_netid
	  
	def casual_name(self):
		if self.user_firstname:
			return self.user_firstname
		else:
			return self.user_netid
	
	def full_name(self):
		if self.user_firstname and self.user_lastname:
			return self.user_firstname + ' ' + self.user_lastname
		elif self.user_netid:
			return self.user_netid
		else:
			return 'noname'
			
	def full_name_suffix(self):
		suf = CalUser.suffix(self)
 		if (len(suf) > 1):
 			return ('%s %s' % (CalUser.full_name(self),suf))
 		else:
			return CalUser.full_name(self)
			
	def set_logged_in(self):
		self.user_last_login = datetime.now()
		self.save()
	
	def add_viewed(self, event):
		self.user_recently_viewed_events.add(event)
		
	def suffix(self):
		if self.user_pustatus.startswith('u'):
			return '\'' + self.user_pustatus.strip('u')
		elif self.user_pustatus.startswith('g'):
			return '*' + self.user_pustatus.strip('g')
		else:
			return " "
		
	
	def is_site_admin(self):
		for admin in SITE_ADMINS:
			if self.user_netid == admin:
				return True
		return False
   


class EventFeature(models.Model):
   feature_name = models.CharField(max_length=50)
   feature_icon = models.ImageField('Icon', upload_to='img/icons')
   
   def __unicode__(self):
      return self.feature_name
      
class EventCategory(models.Model):
   category_name = models.CharField(max_length=50)
   
   def __unicode__(self):
      return self.category_name
            		
      

class EventCluster(models.Model):
   cluster_id = models.AutoField(primary_key=True)             # automatically increments
   cluster_title = models.CharField('Event Title', max_length=255)
   cluster_description = models.TextField('Event Description')
   cluster_date_time_created = models.DateTimeField(auto_now_add=True)
   cluster_user_created = models.ForeignKey(CalUser)               # confirm is actual user
   cluster_image = StdImageField('Image', upload_to='cal/Images', size=(560,800), thumbnail_size=(260,520), blank=True)
   cluster_features = models.ManyToManyField(EventFeature, blank=True, verbose_name='Features')
   cluster_category = models.ForeignKey(EventCategory, verbose_name='Category')
   cluster_rsvp_enabled = models.BooleanField('RSVP is Required to Attend')
   cluster_board_enabled = models.BooleanField('Message Board Enabled') #Whether the message board is activated
   cluster_notify_boardpost = models.BooleanField('Notify Me on Board Posts') #Whether to notify the administrator via email of new board post
   cluster_parent_subscription = models.ForeignKey('WebcalSubscription', null=True)
   
   def __unicode__(self):
      return self.cluster_title

class Event(models.Model):
	# Event_cluster
	event_id = models.AutoField(primary_key=True)              # automatically increments
	event_date_time_created = models.DateTimeField(auto_now_add=True)   
	event_date_time_last_modified = models.DateTimeField(auto_now=True)      
	event_user_last_modified = models.ForeignKey(CalUser)              
 	event_subtitle = models.CharField('Event Subtitle', max_length=255, blank=True)
 	event_subdescription = models.TextField('Event Subdescription', blank=True)
	event_date_time_start = models.DateTimeField('Start Time')            
	event_date_time_end = models.DateTimeField('End Time')               
	event_location = models.CharField('Building', max_length=5, choices=BLDG_CODE, blank=True)  
	event_location_details = models.CharField('Room or Location', max_length=255, blank=True)                 
	event_date_rsvp_deadline = models.DateField('RSVP Deadline', blank=True, null=True)
	event_max_attendance = models.PositiveSmallIntegerField('Maximum Attendees', blank=True, null=True)
	event_attendee_count = models.PositiveSmallIntegerField()                  
	event_cluster = models.ForeignKey(EventCluster)
	event_cancelled = models.BooleanField()
	event_webcal_uid = models.CharField(max_length=100, null=True, unique=True)
		
	def getNextEvent(self):
		return Event.objects.filter(event_date_time_start__gt=self.event_date_time_start).order_by('event_date_time_start')[0]
		
	def getPrevEvent(self):
		return Event.objects.filter(event_date_time_start__lt=self.event_date_time_start).order_by('-event_date_time_start')[0]

	def getConcurrentEvents(self):
		return Event.objects.filter(event_date_time_start=self.event_date_time_start)
	
	def get_absolute_url(self):
	   return our_site+"events/%d" % self.event_id
	
	def __unicode__(self):
		return self.event_cluster.cluster_title + " " + self.event_subtitle
	
	def getAttendeeCount(self):
		return RSVP.objects.filter(rsvp_event = self, rsvp_type = 'Accepted').count()
		
	def getPendingCount(self):
		return RSVP.objects.filter(rsvp_event = self, rsvp_type = 'Pending').count()	
	
	def displayname(self):
		if self.event_subtitle:
			return self.event_cluster.cluster_title + " " + self.event_subtitle
		else:
			return self.event_cluster.cluster_title
			
	def RSSdisplayname(self):
		if self.event_subtitle:
			return self.event_cluster.cluster_title + " " + self.event_subtitle
		else:
			return self.event_cluster.cluster_title
	
	def isAuthorizedModifier(self, user):
		if user == self.event_cluster.cluster_user_created:
			return True
		if user.is_site_admin():
			return True
		return False
	
	def getAbsoluteUrl(self):
		return '/events/%s' % (self.pk)
		
	def isDeleted(self):
		return self.event_date_time_start == dtdeleteflag
		
	def deadlineOkay(self):
		if self.event_date_rsvp_deadline:
			return (self.event_date_rsvp_deadline - date.today()) >= timedelta(0)
		else:
			return True
		
	def moreOkay(self):
		if self.event_max_attendance:
			if (self.event_max_attendance - self.getAttendeeCount()) > 0:
				return True
			else:
				return False
		else:
			return True
	
	def getDate(self):
	  return self.event_date_time_start.date()
	  
	def getTime(self):
	  return self.event_date_time_start.strftime("%l:%M %P")
	  
	def getFormattedStartDate(self):
	  now = datetime.now()
	  if self.event_date_time_start.year == now.year:
	  	return self.event_date_time_start.strftime("%A, %B %e")
	  else:
	  	return self.event_date_time_start.strftime("%A, %B %e, %Y")
	
	def getFormattedShortStartDate(self):
	  now = datetime.now()
	  if self.event_date_time_start.year == now.year:
	  	return self.event_date_time_start.strftime("%B %e")
	  else:
	  	return self.event_date_time_start.strftime("%B %e, %Y")
	
	
	def getEndTime(self):
	  return self.event_date_time_end.strftime("%l:%M %P")
	  
	def getFormattedEndDate(self):
	  now = datetime.now()
	  if self.event_date_time_end.year == now.year:
	  	return self.event_date_time_end.strftime("%A, %B %e")
	  else:
	  	return self.event_date_time_end.strftime("%A, %B %e, %Y")

        def getGCalSDate1(self):
           return self.event_date_time_start.strftime("%Y%m%dT")

        def getGCalSDate2(self):
           adjustedHour = self.event_date_time_start.strftime("%H")
           return int(adjustedHour) + 4

        def getGCalSDate3(self):
           return self.event_date_time_start.strftime("%M%SZ")

        def getGCalEDate1(self):
           return self.event_date_time_end.strftime("%Y%m%dT")

        def getGCalEDate2(self):
           adjustedHour = self.event_date_time_end.strftime("%H")
           return int(adjustedHour) + 4

        def getGCalEDate3(self):
           return self.event_date_time_end.strftime("%M%SZ")

        #       def getGCalEndDate(self):
#         return self.event_date_time_end.strftime("%Y%m%dT%H%M%SZ")

        def getGCalLocation(self):
           if self.event_location_details != "":
               if self.get_event_location_display() != "":
                   return self.get_event_location_display() + ", " + self.event_location_details
               else:
                   return self.event_location_details
           else:
              return self.get_event_location_display()

        def getGCalClusterDes(self):
           return self.event_cluster.cluster_description

        def getGCalEventDes(self):
           return self.event_subdescription

        def getRSSClusterDes(self):
           return unicode(self.event_cluster.cluster_description)

        def getRSSEventDes(self):
           return unicode(self.event_subdescription)       

class BoardMessage(models.Model):
   boardmessage_eventcluster = models.ForeignKey(EventCluster)
   boardmessage_time_posted = models.DateTimeField(auto_now_add=True)
   boardmessage_poster = models.ForeignKey(CalUser)
   boardmessage_title = models.CharField(max_length=50)
   boardmessage_text = models.TextField()
   
   def __unicode__(self):
      return self.boardmessage_text

   def getFormattedTimePosted(self):
      return self.boardmessage_time_posted.strftime("%A, %B %e")

   def getTime(self):
      return self.boardmessage_time_posted.strftime("%l:%M %P")

   def getPoster(self):
      return CalUser.full_name(self.boardmessage_poster)

class RSVP(models.Model):
   rsvp_user = models.ForeignKey(CalUser, related_name="CalUser.rsvp_user_set")
   rsvp_referrer = models.ForeignKey(CalUser, related_name="CalUser.rsvp_referrer_set",null=True, blank=True)
   rsvp_event = models.ForeignKey(Event)
   rsvp_date_created = models.DateTimeField(auto_now_add=True)
   rsvp_reminder_enabled = models.BooleanField()
   rsvp_type = models.CharField(max_length=15) #yes, no, maybe
   
   def accept_url(self):
      return '%suser/invitations/%i/accept' % (our_site, self.pk)
   	
   def decline_url(self):
      return '%suser/invitations/%i/decline' % (our_site, self.pk)
   
   def getStartDate(self):
   	return self.rsvp_event.event_date_time_start
   
   def getTime(self):
	return self.rsvp_event.event_date_time_start.strftime("%l:%M %P")
	
   def getFormattedStartDate(self):
	return self.rsvp_event.event_date_time_start.strftime("%A, %B %e")

   def __unicode__(self):
      return self.rsvp_user.user_netid + "-->" + self.rsvp_event.event_cluster.cluster_title + " :" + self.rsvp_type

MSG_CLASS = {
	0:'error',
	1:'message',
	2:'tips',
	3:'stickynote',
}

class VisitorMessage(models.Model):
	vm_session = models.CharField(max_length = 50)
	vm_date_queued = models.DateTimeField(auto_now_add=True)
	vm_show_after = models.DateTimeField(auto_now_add=True)
	vm_from_page = models.URLField(null = True, blank = True)
	vm_to_page = models.URLField(null = True, blank = True)
 	vm_class = models.IntegerField()
	vm_contents = models.CharField(max_length = 500)
	vm_pending = models.BooleanField()
	
	def deactivate(self):
		self.vm_pending = False
		self.save()
		
	def type(self):
		return MSG_CLASS[self.vm_class]
	
	def __unicode__(self):
		return str(self.vm_date_queued) + '[' + MSG_CLASS[self.vm_class] + ':' + self.vm_from_page + ']'

class UserMessage(models.Model):
	um_user = models.ForeignKey(CalUser)
	um_date_posted = models.DateTimeField(auto_now_add=True)
	um_date_read = models.DateTimeField(null = True, blank = True)
	um_contents = models.CharField(max_length = 500)
	
	def mark_read(self):
		self.um_date_read = datetime.now()
		self.save()
	
	def __unicode__(self):
		return ('Unread' if self.um_date_read == None else 'Read') + ' message for ' + str(self.um_user)

class View(models.Model):
   view_event = models.ForeignKey(Event)
#   view_date_time = models.DateTimeField(auto_now_add=True)
   view_date_time = models.DateTimeField(blank = True, null = True)
   view_viewer = models.ForeignKey(CalUser)
   view_count = models.PositiveSmallIntegerField()

   def __unicode__(self):
      #return str(self.view_event) + ' on: ' + self.event_date_time_start.strtime("%A, %B %e at %l:%M %P")
      return str(self.view_viewer) + ' viewed ' + self.view_event.event_cluster.cluster_title

class WebcalSubscription(models.Model):
	webcal_id = models.AutoField(primary_key=True)
	webcal_url = models.URLField()
	webcal_title = models.CharField(max_length = 50)
	webcal_description = models.CharField(max_length = 500)
	webcal_default_location = models.CharField(max_length = 50)
	webcal_default_category = models.ForeignKey(EventCategory)
	webcal_user_added = models.ForeignKey(CalUser)
	webcal_date_added = models.DateTimeField(auto_now_add=True)
	webcal_date_last_updated = models.DateTimeField(auto_now_add=True)
	
	

