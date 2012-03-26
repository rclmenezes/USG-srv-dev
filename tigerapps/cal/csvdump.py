################################################################
# Project: Princeton Events Calendar
# Author: ]Michael Yaroshefsky 
# Date:    Nov 5, 2010
################################################################
# Title:  csvdump.py
# Info :  returns CSV files for various purposes
################################################################

from django.http import *
from render import render_to_response
from django.contrib.auth import login
import urllib, re
from datetime import datetime, timedelta
from models import *
from cauth import *
from rsvp import *
from dsml import *
from forms import *
from mailer import *
from views_users import *
from views_events import *
from usermsg import MsgMgr
from decorators import login_required
from django.utils.encoding import smart_unicode, smart_str
import csv

@login_required
def downloadAttendeeList(request, event_id):
	try:
		user = current_user(request)
		event = Event.objects.get(pk=event_id)
	except:
		return go_back(request,'Error detected.',0)
	
	if not event.isAuthorizedModifier(user):
		return go_back(request,'You are not authorized to download this file.',0)
	
	response = HttpResponse(mimetype='text/csv')
	response['Content-Disposition'] = 'attachment; filename=attendees.csv'
	
	writer = csv.writer(response)
	writer.writerow(['Date Time of Invitation or Confirmation','NetID', 'Email', 'First Name', 'Last Name', 'Full Name', 'PU Status','Referrer NetID','Referrer Full Name',])
	
	rsvps = RSVP.objects.filter(rsvp_event=event, rsvp_type='Accepted')
	for rsvp in rsvps:
		dtime = rsvp.rsvp_date_created
		netid = rsvp.rsvp_user.user_netid
		email = rsvp.rsvp_user.user_email
		fname = rsvp.rsvp_user.user_firstname
		lname = rsvp.rsvp_user.user_lastname
		fulln = rsvp.rsvp_user.full_name_suffix()
		pusta = rsvp.rsvp_user.user_pustatus
		if rsvp.rsvp_referrer:
			refid = rsvp.rsvp_referrer.user_netid
			refnm = rsvp.rsvp_referrer.full_name_suffix()
		else:
			refid = ''
			refnm = ''
		writer.writerow([dtime, netid, email, fname, lname, fulln, pusta, refid, refnm,])

	return response