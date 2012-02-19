# thirdweek.py
# Meant to send emails to everyone with an open meal exchange on the 21st of every month. Runs from a bash script, which is called by a cronjob

########## Essential for script
import sys,os
sys.path.insert(0,os.path.abspath("/srv/tigerapps"))
import settings
from django.core.management import setup_environ
setup_environ(settings)
###########

from django.core.mail import send_mail, EmailMultiAlternatives
from card.models import *
from smtplib import SMTPException
from django.template.loader import render_to_string
from email.mime.text import MIMEText
from django.utils.html import strip_tags

print '------------------------------'
print 'Running cronjob: thirdweek.py'
print datetime.now()
print ''

memberlist = Member.objects.all()
for member in memberlist:
    hostex = Exchange.objects.filter(meal_1__host=member).filter(meal_2=None)
    guestex = Exchange.objects.filter(meal_1__guest=member, meal_2=None)
    if hostex or guestex:
        html_msg = render_to_string('card/reminder_email.html', {'name':member.full_name, 'hostex':hostex, 'guestex':guestex})
        text_msg = strip_tags(html_msg)

        msg = EmailMultiAlternatives('MealChecker: You have Open Exchanges!', text_msg, 'MealChecker@usg.princeton.edu', [member.email])
        msg.attach_alternative(html_msg, "text/html")
#        try:
        msg.send()
        #except:
        #    pass

        #print msg
        #msg = MIMEText(msg.encode('ascii'), 'html', _charset='ascii')
        #msg['Subject']='MealChecker: You have Open Exchanges!'
        #msg['From']='MealChecker@usg.princeton.edu'
        #msg['To']=member.email
        #msg = msg.as_string()
        #msg = unicode(msg)
        #send_mail('MealChecker: You have Open Exchanges!', msg, 'MealChecker@usg.princeton.edu', [member.email], fail_silently=False)

print 'Done'
print '------------------------------'
print ''
