import os
import re
from django.db import models
from datetime import datetime, date, timedelta
from stdimage import StdImageField
from django.utils.datastructures import SortedDict
from settings import PROJECT_ROOT


FIELDMAP = SortedDict()
FIELDMAP['Netid']='user_netid'
FIELDMAP['First Name']='user_firstname'
FIELDMAP['Nickname']='user_prefname'
FIELDMAP['Middle Name']='user_middlename'
FIELDMAP['Last Name']='user_lastname'
FIELDMAP['Suffix']='user_suffix'
FIELDMAP['Class']='user_class'
FIELDMAP['Degree']='user_degree'
FIELDMAP['Department']='user_dept'
FIELDMAP['College']='user_rescollege'
FIELDMAP['Campus Address']='user_campusaddress'
FIELDMAP['Mailbox']='user_mailbox'
FIELDMAP['Hometown']='user_homecity'
FIELDMAP['Homestate']='user_homestate'
FIELDMAP['Home Country']='user_homecountry'
FIELDMAP['High School']='user_highschool'
FIELDMAP['Birthday']='user_birthday'

DEPT_CODE = {
 	'ANT':'Anthropology',
 	'ARC':'Architecture',
 	'ART':'Art and Archaeology',
 	'AST':'Astrophysical Sciences',
 	'CBE':'Chemical and Biological Engineering',
 	'CHE':'Chemical Engineering',
 	'CHM':'Chemistry',
 	'CEE':'Civil and Environmental Engineering',
 	'CLA':'Classics',
 	'COM':'Comparative Literature',
 	'COS':'Computer Science',
 	'EAS':'East Asian Studies',
 	'EEB':'Ecology and Evolutionary Biology',
 	'ECO':'Economics',
 	'ELE':'Electrical Engineering',
 	'ENG':'English',
 	'FRE':'French and Italian',
 	'GEO':'Geosciences',
 	'GER':'German',
 	'HIS':'History',
 	'MAT':'Mathematics',
 	'MAE':'Mechanical and Aerospace Engineering',
 	'MOL':'Molecular Biology',
 	'MUS':'Music',
 	'NES':'Near Eastern Studies',
 	'ORF':'Operations Research and Financial Engineering',
 	'PHI':'Philosophy',
 	'PHY':'Physics',
 	'POL':'Politics',
 	'PSY':'Psychology',
 	'REL':'Religion',
 	'SLA':'Slavic Languages and Literatures',
 	'SOC':'Sociology',
 	'SPA':'Spanish and Portuguese Languages and Cultures',
 	'WWS':'Woodrow Wilson School of Public and International Affairs'
}

STATE_CODE = {
	'AL':'Alabama',
	'AK':'Alaska',
	'AZ':'Arizona',
	'AR':'Arkansas',
	'CA':'California',
	'CO':'Colorado',
	'CT':'Connecticut',
	'DE':'Delaware',
	'FL':'Florida',
	'GA':'Georgia',
	'HI':'Hawaii',
	'ID':'Idaho',
	'IL':'Illinois',
	'IN':'Indiana',
	'IA':'Iowa',
	'KS':'Kansas',
	'KY':'Kentucky',
	'LA':'Louisiana',
	'ME':'Maine',
	'MD':'Maryland',
	'MA':'Massachusetts',
	'MI':'Michigan',
	'MN':'Minnesota',
	'MS':'Mississippi',
	'MO':'Missouri',
	'MT':'Montana',
	'NE':'Nebraska',
	'NV':'Nevada',
	'NH':'New Hampshire',
	'NJ':'New Jersey',
	'NM':'New Mexico',
	'NY':'New York',
	'NC':'North Carolina',
	'ND':'North Dakota',
	'OH':'Ohio',
	'OK':'Oklahoma',
	'OR':'Oregon',
	'PA':'Pennsylvania',
	'RI':'Rhode Island',
	'SC':'South Carolina',
	'SD':'South Dakota',
	'TN':'Tennessee',
	'TX':'Texas',
	'UT':'Utah',
	'VT':'Vermont',
	'VA':'Virginia',
	'WA':'Washington',
	'WV':'West Virginia',
	'WI':'Wisconsin',
	'WY':'Wyoming'
}

class User(models.Model):
	user_netid = models.CharField(max_length=8, unique=True)
	
	user_puid = models.CharField(max_length=9)
	
	user_email = models.EmailField(max_length=75)
	
	user_firstname = models.CharField(max_length=45)
	
	user_prefname = models.CharField(max_length=45)
	
	user_lastname = models.CharField(max_length=45)
	
	user_middlename = models.CharField(max_length=45)
	
	user_suffix = models.CharField(max_length=10)
	
	user_class = models.CharField(max_length=4)
	
	user_birthday = models.DateField(auto_now=False)
	
	user_degree = models.CharField(max_length=3)
	
	user_dept = models.CharField(max_length=3)
	
	user_rescollege = models.CharField(max_length=15)
	
	user_campusaddress = models.CharField(max_length=25)
	
	user_mailbox = models.IntegerField(max_length=5)
	
	user_homecity = models.CharField(max_length=65)
	
	user_homestate = models.CharField(max_length=2)
	
	user_homecountry = models.CharField(max_length=20)	
	
	user_highschool = models.CharField(max_length=60)
	
	user_message = models.CharField(max_length=140)
	
	#user_image = StdImageField('Image', upload_to='UserImage', size=(200,250), thumbnail_size=(100,125), blank=True)
	
	user_groups = models.ManyToManyField('StudentGroup')
	
	user_last_login = models.DateTimeField(blank=True, null=True)
	
	user_last_update = models.DateTimeField(blank=True, null=True)
	
	user_pageviews = models.IntegerField(max_length=5)
	
	def __unicode__(self):
	  return self.user_netid
	  
	def casual_name(self):
		if len(self.user_prefname) > 0:
			return self.user_prefname
		elif len(self.user_firstname) > 0:
			return self.user_firstname
		else:
			return self.user_netid
	
	def name_suffix(self):
		if len(self.user_suffix) > 0:
			if self.user_suffix == '1st':
				return 'I'
			elif self.user_suffix == '2nd':
  				return 'II'
  			elif self.user_suffix == '3rd':
  				return 'III'
  			else:
  				return self.user_suffix
		else:
			return self.user_suffix
	
 	def full_name(self, suffix=True, middle_name=True, classyear=True):
 		retname = ""
 		if len(self.user_firstname) > 0:
 			retname += self.user_firstname
 		if middle_name and len(self.user_middlename) > 0:
 			retname += " " + self.user_middlename
 		if len(self.user_lastname) > 0:
 			retname += " " + self.user_lastname
 		if suffix and len(self.name_suffix()) > 0:
 			retname += " " + self.name_suffix()
 		if classyear:
 			retname += " "+self.class_suffix()
 		return retname
 		
 	def first_last_name(self):
 		return self.full_name(suffix=False, middle_name=False, classyear=False)
		
	def class_suffix(self):
		return "'"+self.user_class[2:]
		
	def dept_long(self):
		dept = ""
		try:
			dept = DEPT_CODE[self.user_dept]
		except:
			dept - self.user_dept
		return dept
		
	def room_number(self):
		str = self.user_campusaddress.strip()
		parseaddress = str.split()
		if len(parseaddress) > 0:
			return parseaddress[0]
		else:
			return str
       
	def hall(self):
		str = self.user_campusaddress.strip()
		parseaddress = str.split()
		hall_name = ""
		for i in range(len(parseaddress)):
			if i > 0:
				hall_name += parseaddress[i]
				if i < len(parseaddress)-1:
					hall_name += " "
		return hall_name
		
	def photo_url(self):
		photourl =  '/media/facebook/userimage/%s.JPG' % self.user_puid
		
		if os.path.exists(PROJECT_ROOT+photourl):
			return photourl
		else:
			return '/static/facebook/siteimage/nophoto.jpg'		
			
# class UserImage(models.Model):
# 	image_netid = models.ForeignKey(User, related_name = 'User.netid', unique=True)
# 	#image_picture = StdImageField('Image', upload_to='Images', size=(560,800), thumbnail_size=(260,520), blank=True)
# 	image_lastupdated = models.DateTimeField(blank = True, null = True)
	
class PageView(models.Model):
	view_viewer = models.ForeignKey(User, related_name='User.profiles_viewed')
	view_profile = models.ForeignKey(User, related_name='User.profile_viewings')
	view_datetime = models.DateTimeField(blank = True, null = True)
	
	def __unicode__(self):
	  return '%s viewed %s' % (self.view_viewer.full_name(),self.view_profile.full_name())

	def __str__(self):
	  return '%s viewed %s' % (self.view_viewer.full_name(),self.view_profile.full_name())	  

class StudentGroup(models.Model):
	group_name = models.CharField(max_length = 80)
	
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
