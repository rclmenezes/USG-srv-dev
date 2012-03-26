################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  render.py
# Info :  'intercept' a call to render, and do some common things
################################################################

from django import shortcuts
from datetime import datetime
from models import *
from usermsg import MsgMgr, Msg
from globalsettings import our_site

def render_to_response(request, template, dict):
	""" Process every page's common parts """
	if 'user_data' in request.session:
		dict['user_data'] = request.session['user_data']
		#My Events Rightcol
		user_rsvps = RSVP.objects.filter(rsvp_user=dict['user_data'],rsvp_event__event_date_time_start__gte=datetime.now(),rsvp_type='Accepted').order_by('rsvp_event__event_date_time_start')[0:2] 
		first_events = []
		for rsvp in user_rsvps: 
				first_events.append(rsvp.rsvp_event) 
		dict['my_events'] = first_events 


		views = View.objects.filter(view_viewer = dict['user_data']).order_by('view_date_time')[0:3].reverse()
		recently_viewed = []
		for view in views:
			recently_viewed.append(view.view_event)
#		dict['recently_viewed'] = dict['user_data'].user_recently_viewed_events.all()[0:3]
		dict['recently_viewed'] = recently_viewed
			
		#My Invitations Righcol
		user_invites = RSVP.objects.filter(rsvp_user=dict['user_data'],rsvp_event__event_date_time_start__gte=datetime.now(),rsvp_type='Pending').order_by('rsvp_event__event_date_time_start')
# 		upcoming_invites = []
# 		for rsvp in user_invites: 
# 				upcoming_invites.append(rsvp.rsvp_event) 
		dict['my_invites'] = user_invites 
		dict['my_invites_right'] = user_invites[0:2]
		
		umsgs = UserMessage.objects.filter(um_user = dict['user_data'], um_date_read = None)
		dict['umsgs'] = umsgs
		
		dict['n_ur_messages'] = umsgs.count()
	else:
		dict['showrightcol'] = False
		
		
	path = request.path
	if path == '/':
		dict['front'] = ' class="current"'
		dict['uses_lava'] = ' id="topmenu"'	
	elif path == '/today':
		dict['today'] = ' class="current"'
		dict['uses_lava'] = ' id="topmenu"'	
	elif path == '/week':
		dict['week'] = ' class="current"'
		dict['uses_lava'] = ' id="topmenu"'	
	elif path == '/weekend':
		dict['weekend'] = ' class="current"'
		dict['uses_lava'] = ' id="topmenu"'	
	elif path == '/all':
		dict['all'] = ' class="current"'
		dict['uses_lava'] = ' id="topmenu"'
	else:
		dict['lavanone'] = ' class="current"'
		dict['uses_lava'] = ' id="topmenu"'	
	

	#Hot Events Spotlight
	hot_events = Event.objects.exclude(event_date_time_start=dtdeleteflag).filter(event_date_time_end__gte=datetime.now()).order_by('event_attendee_count')[0:3].reverse()
	dict['hot_events'] = hot_events
	
	#Recently Added Spotlight
	recently_added = Event.objects.exclude(event_date_time_start=dtdeleteflag).order_by('event_date_time_created')[0:3].reverse()
	dict['recently_added'] = recently_added
	
	dict['v_messages'] = MsgMgr.iterable(request)
	
	if not 'showrightcol' in dict:
		dict['showrightcol'] = True
	
	dict['our_site'] = our_site
# 	Msg('This site will be undergoing planned maintenance tonight. Sorry for any inconvenience.',1).push(request)
	return shortcuts.render_to_response(template, dict)

