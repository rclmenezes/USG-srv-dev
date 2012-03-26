################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  calmailer.py
# Info :  central hub for outgoing system emails
################################################################

from mailer import *
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from globalsettings import *
from django.http import *
from usermsg import Msg, MsgMgr
from models import *
from views_events import *
import urllib
from django.conf import settings

SYSTEM_ADDRESS = 'Princeton Events Calendar <usg@princeton.edu>'

def email_creator(creator,event):
	""" Send an email to the person who created the event """
	eventurl = event.get_absolute_url()
	try:
		address = urllib.quote('%sevents/%s' % (our_site, event.pk), safe='')
		bitly_address = urllib.urlopen('http://api.bit.ly/v3/shorten?login=princetoneventscalendar&apiKey=R_16e331c21bf86e1f97667dec5608dba6&longUrl=%s&format=txt' % address).readlines()[0]
	except:
		bitly_address = 'none'
	message = render_to_string('cal/email_submittedevent.html', {'site':our_site, 'creator':creator, 'event':event, 'eventurl':eventurl, 'bitly_address':bitly_address})
	sendAdvanced(SYSTEM_ADDRESS,format_address(creator),'Confirmation: \'%s\'' % str(event),message,'Your event was submitted: %s' % eventurl)
	
def email_forwardtocampusevents(creator,event,custommsg):
	""" Send an email to the campus events address """
	eventurl = event.get_absolute_url()
	try:
		address = urllib.quote('%sevents/%s' % (our_site, event.pk), safe='')
		bitly_address = urllib.urlopen('http://api.bit.ly/v3/shorten?login=princetoneventscalendar&apiKey=R_16e331c21bf86e1f97667dec5608dba6&longUrl=%s&format=txt' % address).readlines()[0]
	except:
		bitly_address = 'none'
	message = render_to_string('cal/email_forwardtocampusevents.html', {'site':our_site, 'creator':creator, 'event':event, 'eventurl':eventurl, 'bitly_address':bitly_address, 'custommsg':custommsg})
	sendAdvanced(format_address(creator),'events@princeton.edu','Please list \'%s\'' % str(event),message,'Please add my event to the weekly listing: %s' % eventurl,format_address(creator))

def email_invite(recipient,sender,event,invite):
   """ Send an invitation email to invitee """
   if recipient.user_notify_invitation:
      eventurl = event.get_absolute_url()
      message = render_to_string('cal/email_invite.html', {'site':our_site, 'user':recipient, 'sender':sender, 'event':event, 'eventurl':eventurl, 'invite':invite})
	
      sendAdvanced(format_address(sender),format_address(recipient),'Invitation to \'%s\'' % str(event),message,'I have invited you to this event: %s' % eventurl)

def email_custom_invitation(request, event, message_from, message_to, message_title, message_body):
	#event = Event.objects.get(pk=event_id)
	user = current_user(request)
	eventurl = event.get_absolute_url()
	message = render_to_string('cal/email_custom_invite.html', {'site':our_site, 'body':message_body, 'recipient':message_to, 'sender':message_from, 'event':event, 'eventurl':eventurl, 'user':user})
	sendAdvanced(message_from,message_to,message_title,message,'I have invited you to this event: %s' % eventurl)
	sendAdvanced(message_from,message_from,'Confirmation: %s' % (message_title),message,'I have invited you to this event: %s' % eventurl)
	Msg('Your message was successfully sent to %s, and a confirmation copy was sent to %s.' % (message_to, message_from),1).push(request)
	return HttpResponseRedirect('/events/%s' % event.pk)

def email_event_modification(recipient,modifier,event):
   """ Send an email to attendees that the event was modified """
   eventurl = event.get_absolute_url()
   message = render_to_string('cal/email_event_modification.html', {'site':our_site, 'user':recipient, 'modifier':modifier, 'event':event, 'eventurl':eventurl})
   
   sendAdvanced(SYSTEM_ADDRESS,format_address(recipient),'Modified: \'%s\'' % (event),message,'Visit this page to learn more: %s' % eventurl)
   
   
def email_event_cancellation(recipient,modifier,event):
   """ Send an email to attendees that the event was cancelled """
   eventurl = event.get_absolute_url()
   message = render_to_string('cal/email_event_cancellation.html', {'site':our_site, 'user':recipient, 'modifier':modifier, 'event':event, 'eventurl':eventurl})
   
   sendAdvanced(SYSTEM_ADDRESS,format_address(recipient),'Cancelled: \'%s\'' % (event),message,'Visit this page to learn more: %s' % eventurl)


def email_board_message(recipient, poster, event, contents):
   """ Send an email to the recipient with notification of the newly posted message """
   if event.event_cluster.cluster_notify_boardpost:
      eventurl = event.get_absolute_url()
      message = render_to_string('cal/email_board_message.html', {'site':our_site, 'user':recipient, 'poster':poster, 'event':event,'contents':contents,'eventurl':eventurl})
   
      sendAdvanced(SYSTEM_ADDRESS,format_address(recipient),'New Post: %s' % (event),message,'Visit this page to read it: %s' % eventurl)
      
def email_event_attendees(request, event, sender, message_title, message_body):
   """ Email all attendees of an event with a message """
   if not event:
      return go_back(request,'No event found.',0)
   if not event.isAuthorizedModifier(sender):
      return go_back(request,'Only an event administrator can send these messages.',0)
	
   confirmations = RSVP.objects.filter(rsvp_event = event, rsvp_type = 'Accepted')
   eventurl = event.get_absolute_url()
	
   for confirm in confirmations:
      person = confirm.rsvp_user
      message = render_to_string('cal/email_attendeemsg.html', {'site':our_site, 'user':person,'sender':sender,'msg':message_body,'event':event, 'eventurl':eventurl})
      sendAdvanced(format_address(sender),format_address(person),message_title,message,message_body)
	
   Msg('Your message was successfully sent to the event attendees.',1).push(request)
   return HttpResponseRedirect('/events/%s' % event.pk)
	
def email_today_reminder(user, today):
	""" Send the user an email of his events happening today """
	rsvps = RSVP.objects.filter(rsvp_user = user, rsvp_reminder_enabled = True, rsvp_type='Accepted')
	todayrsvps = []
	for rsvp in rsvps:
		startdate = rsvp.getStartDate()
		if startdate.year == today.year and startdate.month == today.month and startdate.day == today.day:
			todayrsvps.append(rsvp)
	if todayrsvps:
		message = render_to_string('cal/email_reminder.html', {'site':our_site, 'user':user,'rsvps':todayrsvps})
		sendAdvanced(SYSTEM_ADDRESS,format_address(user),"Your Campus Events Today",message,'Daily reminder of your events today.  Log in to %s to view your events today.' % our_site)

def send_cal_email(em_from='usg@princeton.edu', em_recip='usg@princeton.edu', em_subject='Princeton Events Calendar', em_msg=''):
   """ Send a message """
   send(em_from, em_recip, em_subject, em_msg)
   
def format_address(user):
	""" Format the address appropriately with the user's friendly name """
	return '%s <%s>' % (user.full_name(), user.user_email)
