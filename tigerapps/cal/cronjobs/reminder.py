################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  reminder.py
# Info :  called by cron every morning, sends reminder emails
################################################################

########## Essential for script
import sys,os
sys.path.insert(0,os.path.abspath("/srv/tigerapps"))
import settings
from django.core.management import setup_environ
setup_environ(settings)
###########

from django.http import *
from cal.models import *
from cal.calmailer import *
import time
import datetime

print '------------------------------'
print 'Running cronjob: reminder.py'
print datetime.datetime.now()
print ''  

today = datetime.date.today() 
reminderUsers = CalUser.objects.filter(user_reminders_requested = True)
for user in reminderUsers:
 	email_today_reminder(user, today) 	

print 'Done'
print '------------------------------'
print ''
