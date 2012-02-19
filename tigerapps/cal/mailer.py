################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  mailer.py
# Info :  main mail system
# Cred :  based off of Hao Lian's code from the ODUS project
################################################################

# -*- encoding: utf-8 -*-


import os
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import globalsettings
from django.utils.encoding import smart_unicode

HOST = u'localhost'

def send(e_from, e_to, e_subj, msg):
    """Sends htmlMessage string on localhost's SMTP server."""
    msg = smart_unicode(msg)
    e_subj = smart_unicode(e_subj)
    e_from = smart_unicode(e_from)
    e_to = smart_unicode(e_to)

    # Use ASCII if possible, otherwise UTF-8. This is done to avoid
    # base64, which is ugly and not human-readable.
    charset = 'utf8'
    try:
        msg.encode('ascii')
        charset = 'ascii'
    except:
        pass

    msg = MIMEText(msg.encode(charset), 'html', _charset=charset)
    msg['Subject'] = e_subj
    msg['From'] = e_from
    msg['To'] = e_to
    msg = msg.as_string()
	
    try:
        s = smtplib.SMTP(HOST)
        s.sendmail(e_from, [e_to], msg)
        s.quit()
        return 1
    except:
    	return None
    	
def sendAdvanced(e_from, e_to, e_subj, htmlMessage, altMsg, e_cc=None):
	msg = MIMEMultipart('related')
	msg['Subject'] = smart_unicode(e_subj)
	msg['From'] = smart_unicode(e_from)
	msg['To'] = smart_unicode(e_to)
	if e_cc:
		msg['Cc'] = smart_unicode(e_cc)
	mailMonitor = smart_unicode('usg.princeton@gmail.com')
	if e_cc:
		recipients = [e_to] + [mailMonitor] + [msg['Cc']]
	else:
		recipients = [e_to] + [mailMonitor]
		
	
	
	msgAlt = MIMEMultipart('alternative')
	msg.attach(msgAlt)
	
	text = smart_unicode(altMsg)
	part1 = MIMEText(text.encode('utf8'), 'plain', _charset='utf8')
	msgAlt.attach(part1)
	
	imgs = {}
	id = 0
	start = htmlMessage.find('[IMG_EMBED]')
	while start >= 0:
		end = htmlMessage.find('[/IMG_EMBED]')
		if end >= 0:
			substr = htmlMessage[start+11:end]	
			if not substr in imgs:
				imgs[substr] = 'image_%s' % id
				id = id + 1
			htmlMessage = htmlMessage.replace(htmlMessage[start:end+12],'cid:%s' % substr)
		start = htmlMessage.find('[IMG_EMBED]')

	part2 = MIMEText(htmlMessage.encode('utf8'), 'html', _charset='utf8')

	msgAlt.attach(part2)

	for img in imgs:
		fp = open(os.path.expanduser('/srv/tigerapps/%s' % (img)), 'rb')
		msgImg = MIMEImage(fp.read())
		fp.close()
		
		msgImg.add_header('Content-ID', '<%s>' % (img))
		msg.attach(msgImg)
	
	s = smtplib.SMTP(HOST)
	s.sendmail(e_from, recipients, msg.as_string())
	s.quit()	
		
	
