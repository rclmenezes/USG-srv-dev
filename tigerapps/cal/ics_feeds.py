################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  views_events.py
# Info :  rendering pages and executing actions related to events
################################################################

from globalsettings import *
import sys, os
sys.path.append(os.path.expanduser('%s/' % site_root))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings' 

from django.http import *

# from django.contrib.auth import login
import urllib, re
from datetime import datetime, timedelta
from app.models import *
# from cauth import *
# from rsvp import *
# from dsml import *
# from forms import *
# from mailer import *
# from views_users import *
# import vobject
# import cgi
# from usermsg import MsgMgr
# from decorators import login_required
# from django.forms.formsets import formset_factory
# from django.db.models import Q
# from django.utils.encoding import smart_unicode, smart_str

from icalendar import Calendar as VCALENDAR
from icalendar import Event as VEVENT
from icalendar.prop import vDDDTypes

webcal = WebcalSubscription(
	webcal_url = 'http://www.google.com/calendar/ical/princetonusg.com_0jbjnnqm6d7tipveh3aerr6p8c%40group.calendar.google.com/public/basic.ics',
	webcal_title = 'Academic Calendar',
	webcal_description = 'List of events for the academic calendar',
	webcal_default_location = 'Princeton University',
	webcal_default_category = EventCategory.objects.get(category_name='Other'),
	webcal_user_added = CalUser.objects.get(user_netid='yaro')
	)
webcal.save()

webcal2 = WebcalSubscription(
	webcal_url = ' http://www.google.com/calendar/ical/cloister%40princeton.edu/public/basic.ics',
	webcal_title = 'Cloister Calendar',
	webcal_description = 'List of events for cloister',
	webcal_default_location = 'Cloister',
	webcal_default_category = EventCategory.objects.get(category_name='Other'),
	webcal_user_added = CalUser.objects.get(user_netid='yaro')
	)
webcal2.save()


def AddOrUpdateWebcal(webcal):
	calString = urllib.urlopen(webcal.webcal_url).read()
	cal = VCALENDAR.from_string(calString)
	eventCluster = EventCluster(
			cluster_title = webcal.webcal_title,
			cluster_description = webcal.webcal_description,
			cluster_user_created = webcal.webcal_user_added,
			cluster_category = webcal.webcal_default_category,
			cluster_rsvp_enabled = False,
			cluster_board_enabled = True,
			cluster_notify_boardpost = False,
		)
	eventCluster.save()
	
	for component in cal.walk():
		if(component.name == 'VEVENT'):
			valid = True
			proplist = {}
			REQ_PROPS = ('UID','SUMMARY','DTSTART','DTEND')
			for prop in component.property_items():
				proplist[prop[0]] = prop[1]

			for rprop in REQ_PROPS:
				if rprop not in proplist:
					print 'MISSING %s' % rprop
					valid = False

			if valid:
				try:
					updateEvent = Event.objects.get(event_webcal_uid = proplist['UID'])
					print 'I found my old friend, %s' % proplist['UID']
				except:
					dtstart = vDDDTypes.from_ical(proplist['DTSTART'].ical())
					dtend = vDDDTypes.from_ical(proplist['DTEND'].ical())
					add_event = Event(
						event_webcal_uid = proplist['UID'],
						event_user_last_modified = CalUser.objects.get(user_netid='yaro'),
						event_subtitle = proplist['SUMMARY'],
						event_subdescription = proplist.get('DESCRIPTION','No description provided.'),
						event_date_time_start = dtstart,
						event_date_time_end = dtend,
						event_location_details = proplist.get('LOCATION',''),
						event_cluster = eventCluster,
						event_cancelled = False,
						event_attendee_count = 0,)
					add_event.save()

AddOrUpdateWebcal(webcal);
#AddOrUpdateWebcal(webcal2);

# calString = urllib.urlopen('http://www.google.com/calendar/ical/princetonusg.com_0jbjnnqm6d7tipveh3aerr6p8c%40group.calendar.google.com/public/basic.ics').read()
# #calString = urllib.urlopen('http://www.princeton.edu/events/feeds/calendar.ics?category=Exhibits').read()
# print calString
# print 'Done!'
# #print calString
# cal = VCALENDAR.from_string(calString)
# 
# EventCluster.objects.filter(cluster_title = 'Experimental').delete()
# 
# for component in cal.walk():
# 	if(component.name == 'VCALENDAR'):
# 		print "Calendar"
# 		eventCluster = EventCluster(
# 			cluster_title = 'Academic Calendar',
# 			cluster_description = 'An event imported from the Princeton Academics Calendar published by the USG.',
# 			cluster_user_created = CalUser.objects.get(user_netid='yaro'),
# 			cluster_category = EventCategory.objects.get(category_name='Other'),
# 			cluster_rsvp_enabled = False,
# 			cluster_board_enabled = True,
# 			cluster_notify_boardpost = False,
# 		)
# 		eventCluster.save()
# 	elif(component.name == 'VEVENT'):
#  		#print 'VEVENT: %s' % component.property_items()
# 		
# 		proplist = {}
# 		
# 		REQ_PROPS = ('UID','SUMMARY','DTSTART','DTEND')
# 		for prop in component.property_items():
# 			proplist[prop[0]] = prop[1]
# 		#print proplist
# 		for rprop in REQ_PROPS:
# 			if rprop not in proplist:
# 				print 'MISSING %s' % rprop
# 		#print proplist['DTSTART']
# 		#print proplist['DTSTART'][0:4]
# 		#print proplist['DTSTART'][4:6]
# 		#print proplist['DTSTART'][6:8]
# 		#datetime dt = new datetime(year=proplist['DTSTART'][0:4],month=proplist['DTSTART'][4:6],day=proplist['DTSTART'][6:8])
# 		#print vTime.from_ical(proplist['DTSTART'])
# 		dtstart = vDDDTypes.from_ical(proplist['DTSTART'].ical())
# 		dtend = vDDDTypes.from_ical(proplist['DTEND'].ical())
# 		#dt = new datetime(vDDDTypes.from_ical(proplist['DTSTART']))
# 		#print type(dt)
# 		add_event = Event(
# 			event_user_last_modified = CalUser.objects.get(user_netid='yaro'),
# 			event_subtitle = proplist['SUMMARY'],
# 			event_subdescription = proplist.get('DESCRIPTION','No description provided.'),
# 			event_date_time_start = dtstart,
# 			event_date_time_end = dtend,
# 			event_location_details = proplist.get('LOCATION',''),
# 			event_cluster = eventCluster,
# 			event_cancelled = False,
# 			event_attendee_count = 0)
# 		add_event.save()
# 
# 			
# def acceptable_VCALENDAR(proplist):
# 	if('X-WR-CALNAME' not in proplist):
# 		return False
# 	return True
# 
# def acceptable_VEVENT(proplist):
# 	REQ_PROPS = ('UID','SUMMARY','DTSTART','DTEND')
# 	for required_property in REQ_PROPS:
# 		if(required_propoerty not in proplist):
# 			return False
# 	return True
		


# 
# 	cal = vobject.iCalendar()
# 	cal.add('CALSCALE').value = 'GREGORIAN'
# 	cal.add('METHOD').value = 'PUBLISH'
# 	cal.add('X-WR-CALNAME').value = '%s Events' % user.full_name()
# 	cal.add('X-WR-TIMEZONE').value = 'America/New_York'
# 	cal.add('X-WR-CALDESC').value = 'Events submitted by %s to the Princeton Events Calendar, %s.' % (user.full_name(), our_site)
# 	cal.add('X-PUBLISHED-TTL').value = 'PT1H'
# 	
# 	publishedEvents = Event.objects.filter(event_cluster__cluster_user_created=user).order_by('event_date_time_start')
# 
# 	for event in publishedEvents:
# 		vevent = cal.add('VEVENT')
# 		vevent.add('UID').value = "%i@%s" % (event.event_id, our_email)
# 		vevent.add('RELATED-TO').value = 'RELTYPE=CHILD:%irecur@%s' % (event.event_cluster.cluster_id, our_email)
# 		vevent.add('SUMMARY').value = smart_unicode(str(event))
# 		vevent.add('DTSTART').value = event.event_date_time_start
# 		vevent.add('DTEND').value = event.event_date_time_end
# 		vevent.add('CREATED').value = event.event_cluster.cluster_date_time_created
# 		vevent.add('LAST-MODIFIED').value = event.event_date_time_last_modified
# 		if event.event_cancelled == True:
# 			vevent.add('STATUS').value = "CANCELLED"
# 		else:
# 			vevent.add('STATUS').value = "CONFIRMED"
# 		vevent.add('URL').value = our_site + event.get_absolute_url()
# 		vevent.add('TRANSP').value = 'TRANSPARENT'
# 		vevent.add('ORGANIZER').value = '%s' % (event.event_cluster.cluster_user_created.user_email)
# 		
# 		vevent.add('LOCATION').value = unicode(event.getGCalLocation())
# 		vevent.add('DESCRIPTION').value = unicode(event.getGCalClusterDes() + "\n\n" + event.getGCalEventDes())
# 
# 	icalstream = cal.serialize()
# 	response = HttpResponse(icalstream, mimetype='text/calendar')
# 	response['Content-Type'] = 'text/calendar; charset=utf-8'
# 	response['Connection'] = 'close'
# 	response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
# 	response['Pragma'] = 'no-cache'
# 	return response
