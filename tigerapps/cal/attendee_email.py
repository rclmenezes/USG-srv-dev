################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  attendee_email.py
# Info :  for emailing all attendees of an event
################################################################

from django.http import *
from render import render_to_response
from django.contrib.auth import login
import urllib, re, datetime
from models import *
from calmailer import email_event_attendees
from cauth import *
from rsvp import *
from forms import *
from mailer import *
from usermsg import MsgMgr
from decorators import login_required
from views_events import *

@login_required
def form_email_attendees(request, event_id):
  """Show form for emailing attendees"""
  try:
  	myEvent = Event.objects.get(event_id=event_id)
  except:
  	return go_back(request, 'Error: No event found',0)
  attendee_count = myEvent.event_attendee_count
  user = current_user(request)
  if not myEvent.isAuthorizedModifier(user):
	Msg('Only an event administrator can use this feature to send emails to all attendees.',0).push(request)
	return HttpResponseRedirect('/events/%s' % event_id)
  elif attendee_count == 0:
	Msg('There are no confirmed attendees... yet!',0).push(request)
	return HttpResponseRedirect('/events/%s' % event_id)
  else:
	dict = {'event': myEvent}
	dict['whoscoming'] = RSVP.objects.filter(rsvp_event = myEvent, rsvp_type = 'Accepted')
	return render_to_response(request,"cal/email_attendees.html", dict)

@login_required
def email_attendees(request, event_id):
	"""Process email for attendees"""
	if request.method == 'POST':
		message_title = request.POST.get('subject',None)
		message_body = request.POST.get('message',None)
		myEvent = Event.objects.get(event_id=event_id)
		return email_event_attendees(request, myEvent, current_user(request), message_title, message_body)
	else:
		return go_back(request, 'Invalid request.',0)
	
	