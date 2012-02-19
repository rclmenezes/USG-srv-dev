import os
import sys
from globalsettings import *
sys.path.append(os.path.expanduser('%s/' % site_root))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings' 
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from django.template.loader import render_to_string
from app.globalsettings import *
from django.http import *
from app.models import *

from mailer import sendAdvanced

user = CalUser.objects.get(user_netid = 'yaro')
sender = CalUser.objects.get(user_netid = 'yaro')
event = Event.objects.get(pk = 2)
eventurl = event.get_absolute_url()
message = render_to_string('cal/email_invite.html', {'site':our_site, 'user':user, 'sender':sender, 'event':event, 'eventurl':eventurl})

sendAdvanced('yaro@princeton.edu','yaro@princeton.edu','Check this out',message,'In case you cannot read the actual message')
# 
# 
# HOST = u'localhost'
# 
# 
# msg = MIMEMultipart('related')
# msg['Subject'] = 'Hey!'
# msg['From'] = sender.user_email
# msg['To'] = user.user_email
# 
# 
# msgAlt = MIMEMultipart('alternative')
# msg.attach(msgAlt)
# 
# text = 'Hello!\n1\n2\n3'
# part1 = MIMEText(text, 'plain')
# msgAlt.attach(part1)
# 
# imgs = {}
# id = 0
# start = message.find('[IMG_EMBED]')
# while start >= 0:
# 	end = message.find('[/IMG_EMBED]')
# 	if end >= 0:
# 		substr = message[start+11:end]
# 		if not substr in imgs:
# 			imgs[substr] = 'image_%s' % id
# 			id = id + 1
# 		message = message.replace(message[start:end+12],'cid:%s' % imgs[substr])
# 	start = message.find('[IMG_EMBED]')
# 
# # charset = 'utf8'
# # try:
# # 	message.encode('ascii')
# # 	charset = 'ascii'
# # except:
# # 	pass
# 
# # #html = """<html><head></head><body><p>Hi!</p><p><img src="cid:image1"></p></body></html?"""
# part2 = MIMEText(message, 'html')
# msgAlt.attach(part2)
# 
# for img in imgs:
# 	fp = open(os.path.expanduser('~/pcal_dev/%s' % (img)), 'rb')
# 	msgImg = MIMEImage(fp.read())
# 	fp.close()
# 	
# 	msgImg.add_header('Content-ID', '<%s>' % (imgs[img]))
# 	msg.attach(msgImg)
# 
# s = smtplib.SMTP(HOST)
# s.sendmail(sender.user_email, user.user_email, msg.as_string())
# s.quit()	
# 	
