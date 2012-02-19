import sys, os

# hardcode path to be the same as the one django uses
sys.path.insert(0,'/srv/tigerapps/groups')
sys.path.insert(0,'/srv/tigerapps')
sys.path.insert(0,'/srv/tigerapps/groups/cronjobs')

# import correct settings location and place to find correct django model
os.environ['DJANGO_SETTINGS_MODULE']='settings'
os.environ['PYTHONPATH']='/usr/local/lib/python2.6/dist-packages/django:'

from datetime import datetime,date
import random
import string
from groups.models import *
from email_msg import *
from globalsettings import SITE_URL, SITE_EMAIL, EMAIL_HEADER_PREFIX, ADMIN_EMAILS
from django.core.mail import send_mail

print '------------------------------'
print 'Running cronjob: deactivate.py'
print datetime.now()
print ''  

groups = Group.objects.filter(active_status='R')

print 'Inactive groups: '
for g in groups:
    print g.name
print ''

list = []
for group in groups:
    # Put in limbo
    group.active_status = 'I'
    group.date_last_active = date.today()
    group.save()
    
    print 'Changed %s status'%group.name

    # get officer emails
    officers = Membership.objects.filter(group=group,type='O')
    for o in officers:
        list.append(o.student.email)
        
    # send email
    send_mail(EMAIL_HEADER_PREFIX+'%s Deactivated'%group.name, INACTIVE_EMAIL % (group.name,group.url), SITE_EMAIL, list, fail_silently=False)

    print 'emailed: '
    for l in list:
        print l
    print ''

# email the admins
send_mail(EMAIL_HEADER_PREFIX+'Cron Notification', 'Job: deactivate.py\nRan on: %s\nView output in cron_log on server'%datetime.now(), SITE_EMAIL, ADMIN_EMAILS, fail_silently=False)

print 'Done'
print '------------------------------'
print ''
