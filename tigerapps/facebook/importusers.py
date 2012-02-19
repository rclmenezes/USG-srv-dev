import sys, os, traceback
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"

import csv
import time
from csv import *
from datetime import *
from app.models import *

header = ('Emplid','Netid','Last Name','First Name','Middle Name','Suffix','Birthdate','Class','Frist Box','Campus Address','Campus City','Campus State','Campus Zip','Campus Phone','Home Address1','Home Address2','Home City','Home State','Home Zip','Nation','Degree','Dept','Email','College','External Organization - Long Description')

users = open( "Stdntdata.txt", "rU" )
csvReader = csv.DictReader(users, fieldnames=header)


index = 0

for data in csvReader:
	if index > 7000:
		break
	else:
		try:
			print data["Netid"]
			print data["Emplid"]
			try:
				fb = data["Frist Box"].replace("Box ", "")
			except:
				try:
					fb = data["Frist Box"]
				except:
					fb = 0
			if fb == '':
				fb = 0
			newbie = User()
			newbie.user_netid = data["Netid"]
			newbie.user_puid = data["Emplid"]
			newbie.user_email = data["Email"]
			newbie.user_firstname = data["First Name"].encode('ascii', 'replace')
			newbie.user_prefname = data["First Name"].encode('ascii', 'replace')
			newbie.user_lastname = data["Last Name"].encode('ascii', 'replace')
			newbie.user_middlename = data["Middle Name"].encode('ascii', 'replace')
			newbie.user_suffix = data["Suffix"].encode('ascii', 'replace')
			newbie.user_class = data["Class"]
			newbie.user_birthday = datetime.strptime(data["Birthdate"], "%m/%d/%y")
			newbie.user_degree = data["Degree"]
			newbie.user_dept = data["Dept"]
			newbie.user_rescollege = data["College"]
			newbie.user_campusaddress = data["Campus Address"]
			newbie.user_mailbox = fb
			newbie.user_homecity = data["Home City"].encode('ascii', 'replace')
			newbie.user_homestate = data["Home State"].encode('ascii', 'replace')
			newbie.user_homecountry = data["Nation"].encode('ascii', 'replace')
			newbie.user_highschool = data["External Organization - Long Description"].encode('ascii', 'replace')
			newbie.user_message = ""
			newbie.user_image = None
			newbie.user_last_login = datetime.now()
			newbie.user_last_update = datetime.now()
			newbie.user_pageviews = 0
			#newbie.save()
			index += 1
		except:
			print "Exception in user code:"
			print '-'*60
			traceback.print_exc(file=sys.stdout)
			print '-'*60

users.close()
