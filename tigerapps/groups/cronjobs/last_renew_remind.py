import sys, os

# hardcode path to be the same as the one django uses
sys.path.insert(0,'/srv/tigerapps/groups')
sys.path.insert(0,'/srv/tigerapps')
sys.path.insert(0,'/srv/tigerapps/groups/cronjobs')

# import correct settings location and place to find correct django model
os.environ['DJANGO_SETTINGS_MODULE']='settings'
os.environ['PYTHONPATH']='/usr/local/lib/python2.6/dist-packages/django:'

from datetime import datetime
import random
import string
from groups.models import *
from email_msg import *
from globalsettings import SITE_URL, SITE_EMAIL, EMAIL_HEADER_PREFIX, ADMIN_EMAILS
from django.core.mail import send_mail

print '------------------------------'
print 'Running cronjob: last_renew_remind.py'
print datetime.now()
print ''  

groups = Group.objects.filter(active_status='R')

print 'Remind groups: '
for g in groups:
    print g.name
print ''

list = []
for group in groups:
    print 'Group: %s'%group.name

    # get officer emails
    officers = Membership.objects.filter(group=group,type='O')
    for o in officers:
        list.append(o.student.email)
        
    # send email
    send_mail(EMAIL_HEADER_PREFIX+'REMINDER: Renew %s Profile'%group.name, GROUP_RENEWAL_LAST_REMIND_EMAIL % (group.name,group.url), SITE_EMAIL, list, fail_silently=False)

    print 'emailed: '
    for l in list:
        print l
    print ''

# email the admins
send_mail(EMAIL_HEADER_PREFIX+'Cron Notification', 'Job: last_renew_remind.py\nRan on: %s\nView output in cron_log on server'%datetime.now(), SITE_EMAIL, ADMIN_EMAILS, fail_silently=False)

print 'Done'
print '------------------------------'
print ''
