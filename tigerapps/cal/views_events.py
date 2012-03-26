################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  views_events.py
# Info :  rendering pages and executing actions related to events
################################################################

from groups.models import *
from groups.email_msg import FEED_NOTIFICATION_EMAIL
from groups.globalsettings import SITE_EMAIL,EMAIL_HEADER_PREFIX
from cal.globalsettings import our_site, our_email
from django.core.mail import send_mail

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
import vobject
import cgi
from usermsg import MsgMgr
from decorators import login_required
from django.forms.formsets import formset_factory
from django.db.models import Q
from django.utils.encoding import smart_unicode, smart_str
from django.template import Context, loader

def events(request):
	dict = {}
	dict['tabtitle'] = "Upcoming Events"
	all_events = Event.objects.filter(event_date_time_start__gte=datetime.now()).order_by('event_date_time_start')[0:7]
	
	dict['poster_events'] = Event.objects.filter(event_date_time_start__gte=datetime.now(), event_cluster__cluster_image__isnull=False, ).exclude(event_cluster__cluster_image='').order_by('event_date_time_start')[0:7]
	dict['hotest_events'] = Event.objects.filter(event_attendee_count__gte=1, event_date_time_start__gte=datetime.now(), event_cluster__cluster_image__isnull=False, ).exclude(event_cluster__cluster_image='').order_by('-event_attendee_count')[0:7]

	
	return event_processing_dicts(request, all_events, dict, template="cal/front.html")

def todays_events(request):
   dict = {}
   dict['tabtitle'] = "Events Today"
   dict['filter'] = 'on'
   now = datetime.today()
   now_day = now.day
   now_month = now.month
   now_year = now.year
   
   return events_date(request, now_year, now_month, now_day)
   
#   today_events = Event.objects.filter(event_date_time_start__day=now_day,event_date_time_start__month=now_month, event_date_time_start__year=now_year).order_by('event_date_time_start')
#   date_string = (datetime.today().strftime("%A, %B %e"))
#   my_dates = []
#   events_on_date = {}
#   my_dates.append(date_string)
#   events_on_date[date_string] = []
#   usr = current_user(request)
#   for event in today_events:
#      if usr:	
#         try:
#            events_on_date[date_string].append((event,RSVP.objects.get(rsvp_event = event, rsvp_user = usr)))
#         except:
#            events_on_date[date_string].append((event,None))
#      else:
#         events_on_date[date_string].append((event,None))
           
#   dict['all_my_dates'] = my_dates
#   dict['events_on_date'] = events_on_date

#   dict['site'] = request.path	
   
#   feat_list = EventFeature.objects.all()
#   dict['feat_opts'] = feat_list
	
#   return render_to_response(request, "myevents.html", dict);


def weeks_events(request):
        dict = {}
        dict['tabtitle'] = "Events This Week"
        today = datetime.today()
        midnight = datetime(today.year, today.month, today.day, 0, 0, 0)
        next_week = timedelta(weeks=1)
        weeks_events = Event.objects.filter(event_date_time_start__gte=midnight,event_date_time_start__lte=midnight + next_week).order_by('event_date_time_start')
        return event_processing_dicts(request, weeks_events, dict)

def weekends_events(request):
        dict = {}
        dict['tabtitle'] = "Events This Weekend"
        next_week = timedelta(weeks=1)
        today = datetime.today()
        midnight = datetime(today.year, today.month, today.day, 0, 0, 0)
        weeks_events = Event.objects.filter(Q(event_date_time_start__gte=midnight) & Q(event_date_time_start__lte=midnight + next_week) & (Q(event_date_time_start__week_day=1) | Q(event_date_time_start__week_day=6) | Q(event_date_time_start__week_day=7))).order_by('event_date_time_start')

        return event_processing_dicts(request, weeks_events, dict)

def all_events(request):
	dict = {}
	dict['tabtitle'] = "All Events"
	dict['feedurl'] = request.path + '.ics'
	next_week = timedelta(weeks=1)
	all_events = Event.objects.filter(event_date_time_start__gte=datetime.now()).order_by('event_date_time_start')

	return event_processing_dicts(request, all_events, dict)

def events_date(request, year, month, day):
        dict = {}
        date = datetime(int(year), int(month), int(day))
        if not date:
		     return render_to_response(request, "cal/myevents.html", dict);
        dict['tabtitle'] = "Events on %s" % (date.strftime("%A, %B %e"))
        dict['filter'] = 'on'
#        now = datetime.today()
#        now_day = now.day
#        now_month = now.month
#        now_year = now.year              #check if valid date
#	date = datetime(int(year), int(month), int(day)) #new
#	if not date:
#		return render_to_response(request, "myevents.html", dict);

	now_day = date.day #new
	now_month = date.month #new
	now_year = date.year #new
	
	today_events = Event.objects.filter(event_date_time_start__day=now_day,event_date_time_start__month=now_month, event_date_time_start__year=now_year).order_by('event_date_time_start')
        #today_events = apply_filter(request, today_events)
        date_string = date.strftime("%A, %B %e")    # changed
        my_dates = []
        events_on_date = {}
        my_dates.append(date_string)
        events_on_date[date_string] = []
        usr = current_user(request)
        for event in today_events:
                if usr:
                        try:
                                events_on_date[date_string].append((event,RSVP.objects.get(rsvp_event = event, rsvp_user = usr)))
                        except:
                                events_on_date[date_string].append((event,None))
                else:
                        events_on_date[date_string].append((event,None))
			
	dict['all_my_dates'] = my_dates
        dict['events_on_date'] = events_on_date

        cat_list = EventCategory.objects.all()
        dict['cat_opts'] = cat_list

        feat_list = EventFeature.objects.all()
        dict['feat_opts'] = feat_list

        dict['site'] = request.path

        return render_to_response(request, "cal/myevents.html", dict);

def filterByFeature(request, feature):
	try:
		dict = {}
		dict['tabtitle'] = "Events Featuring %s" % feature
		dict['feedurl'] = request.path + '.ics'
		feat = EventFeature.objects.get(feature_name=feature)
		events = Event.objects.filter(event_date_time_start__gte=datetime.now()).filter(event_cluster__cluster_features=feat).order_by('event_date_time_start')
		return event_processing_dicts(request, events, dict)
	except:
		return go_back(request,'Error detected.%s' %feature,0)

def filterByCategory(request, category):
	try:
		dict = {}
		dict['tabtitle'] = "Events in the  \'%s\' Category" % category
		dict['feedurl'] = request.path + '.ics'
		cat = EventCategory.objects.get(category_name=category)
		events = Event.objects.filter(event_date_time_start__gte=datetime.now()).filter(event_cluster__cluster_category=cat).order_by('event_date_time_start')
		return event_processing_dicts(request, events, dict)
	except:
		return go_back(request,'Error detected.%s' %category,0)		

def filterByUser(request, user):
	try:
		caluser = CalUser.objects.get(user_netid=user)
	except:
		return go_back(request,'Could not find user with NetID \'%s\' who has visited the calendar site.' %user,0)
	dict = {}
	dict['tabtitle'] = "Events Submitted by %s" % caluser.full_name();
	dict['feedurl'] = request.path + '.ics'
	events = Event.objects.filter(event_date_time_start__gte=datetime.now()).filter(event_cluster__cluster_user_created=caluser).order_by('event_date_time_start')
	return event_processing_dicts(request, events, dict)
	
def showHotEvents(request):
	dict = {}
	dict['tabtitle'] = "Top 10 Hot Upcoming Events"
	dict['subtitle'] = "Ordered by number of confirmed attendees"
	events = Event.objects.filter(event_date_time_start__gte=datetime.now()).filter(event_attendee_count__gte=1).order_by('-event_attendee_count')[0:10]
	return event_list_view(request, events, dict)
	
def showRecentlyAddedEvents(request):
	dict = {}
	dict['tabtitle'] = "10 Most Recently Added Upcoming Events"
	dict['subtitle'] = "Ordered by date submitted"
	dict['flag_dateadded'] = True
	events = Event.objects.filter(event_date_time_start__gte=datetime.now()).order_by('-event_date_time_created')[0:10]
	return event_list_view(request, events, dict)	

def showRecentlyViewedEvents(request):
	user = current_user(request)
	dict = {}
	dict['tabtitle'] = "Your 10 Most Recently Viewed Events"
	dict['subtitle'] = "Ordered by date viewed"
	dict['flag_dateviewed'] = True
	dict['flag_dateadded'] = True
	views = View.objects.filter(view_viewer=user).order_by('-view_date_time')[0:10]
	events = []
	dict['views'] = {}
	for v in views:
		events.append(v.view_event)
		dict['views'][v.view_event] = v.view_date_time
	return event_list_view(request, events, dict)

def getMatchingRSVP(event_pk, user):
	return RSVP.objects.get(rsvp_event = Event.objects.get(pk=event_pk),rsvp_user = user)

def event_list_view(request, events, dict):
	dict['events'] = events
	feat_list = EventFeature.objects.all()
	dict['feat_opts'] = feat_list	
	return render_to_response(request, "cal/eventlist.html", dict)

def event_processing_dicts(request, array, dict, template="cal/myevents.html"):

	today = datetime.now()
	my_dates = []
	events_on_date = {}
	usr = current_user(request)
	for event in array:
		if event.event_date_time_start.year == today.year:
			date_string = event.event_date_time_start.strftime("%A, %B %e")
		else:
			date_string = event.event_date_time_start.strftime("%A, %B %e, %Y")
		if date_string not in my_dates:
			my_dates.append(date_string)
			events_on_date[date_string] = []
		if usr:	
			try:
				events_on_date[date_string].append((event,RSVP.objects.get(rsvp_event = event, rsvp_user = usr)))
			except:
				events_on_date[date_string].append((event,None))
		else:
			events_on_date[date_string].append((event,None))
	dict['all_my_dates'] = my_dates
	dict['events_on_date'] = events_on_date
	
	cat_list = EventCategory.objects.all()
	dict['cat_opts'] = cat_list

	feat_list = EventFeature.objects.all()
	dict['feat_opts'] = feat_list	
	
	return render_to_response(request, template, dict)

def event_processing(request, array, dict):
	my_dates = []
	events_on_date = {}
	for event in array:
		date_string = event.event_date_time_start.strftime("%A, %B %e")
	if date_string not in my_dates:
		  my_dates.append(date_string)
		  events_on_date[date_string] = []
	events_on_date[date_string].append(event)

	dict['all_my_dates'] = my_dates
	dict['events_on_date'] = events_on_date
	
	cat_list = EventCategory.objects.all()
	dict['cat_opts'] = cat_list

	feat_list = EventFeature.objects.all()
	dict['feat_opts'] = feat_list

	dict['site'] = request.path
	
	return render_to_response(request, 'cal/myevents.html', dict)


@login_required
def confirm(request, event_id):
	try:
		event = Event.objects.get(event_id = event_id)
	except:
		return go_back(request,'That event could not be found.',0)	
	user = current_user(request)
	referrer = None
	reminder = True
	confirm_attendance(user,referrer,event,reminder).push(request)
	return HttpResponseRedirect('/events/%s' % (event_id));


@login_required
def unconfirm(request, event_id):
	user = current_user(request)
	try:
		event = Event.objects.get(event_id = event_id)
	except:
		return go_back(request,'That event could not be found.',0)
	unconfirm_attendance(user,event).push(request)
	return HttpResponseRedirect('/events/%s' % (event_id))


@login_required
def events_description(request, event_id):
		
		myEvent = Event.objects.get(event_id=event_id)
		myEvent.event_attendee_count = myEvent.getAttendeeCount()
		myEvent.save()
		

		associatedEvents = Event.objects.exclude(event_date_time_start=dtdeleteflag).filter(event_cluster = myEvent.event_cluster).exclude(pk=myEvent.pk).order_by('event_date_time_start')
		boardMessages = BoardMessage.objects.filter(boardmessage_eventcluster = myEvent.event_cluster).order_by('boardmessage_time_posted').reverse()
		dict = {'event': myEvent, 'associatedEvents': associatedEvents, 'boardMessages': boardMessages}

		
		try:
			dict['prev_event'] = myEvent.getPrevEvent()
		except:
			pass
		try:
			dict['next_event'] = myEvent.getNextEvent()
		except:
			pass
		try:
			dict['conc_events'] = myEvent.getConcurrentEvents()
		except:
			pass
			
		if request.method == 'GET' and 'forwardtoevents' in request.GET:
			dict['forwardtoevents'] = True
		else:
			dict['forwardtoevents'] = False
			
		
			
		public_guests = RSVP.objects.filter(rsvp_event = myEvent, rsvp_type = 'Accepted', rsvp_user__user_privacy_enabled = False).order_by('rsvp_user__user_netid')
		private_guests = RSVP.objects.filter(rsvp_event = myEvent, rsvp_type = 'Accepted', rsvp_user__user_privacy_enabled = True).order_by('rsvp_user__user_netid')
		
		user = current_user(request)
		dict['authorized'] = myEvent.isAuthorizedModifier(user)		
		
		n_public_guests = public_guests.count()
		
		max_disp = 5;
		
		if n_public_guests > max_disp+1:
			dict['whoscoming'] = public_guests[0:max_disp]
			dict['whoscoming_extra'] = (n_public_guests - max_disp) + private_guests.count()
			dict['show_extra'] = True
		else:
			dict['whoscoming'] = public_guests
			dict['whoscoming_extra'] =  private_guests.count()
			dict['show_extra'] = False
			
			
		
		dict['showrightcol'] = False
		
		if dict['authorized']:
			dict['whoscoming'] = RSVP.objects.filter(rsvp_event = myEvent, rsvp_type = 'Accepted').order_by('rsvp_user__user_netid')
			dict['whoscoming_extra'] = 0
			dict['show_extra'] = False
			
		user.add_viewed(myEvent)

		dict['open_invites'] = RSVP.objects.filter(rsvp_event = myEvent, rsvp_type = 'Pending').count()

		try: 
			previous_view = View.objects.get(view_viewer = user, view_event = myEvent)
			previous_view.view_count = previous_view.view_count + 1
			previous_view.view_date_time = datetime.now()
			previous_view.save()
		except:
			new_view = View(view_event = myEvent, 
					view_date_time = datetime.now(),
					view_viewer=user, 
					view_count = 1)
			new_view.save()
		try: 
			dict['users_rsvp'] = RSVP.objects.get(rsvp_user = user, rsvp_event = myEvent)
			if 'showrsvp' in request.GET:
				Msg('%s has invited you to this event. <a href="/user/invitations/%s/accept/">Accept?</a> <a href="/user/invitations/%s/decline/">Decline?</a> ' % (dict['users_rsvp'].rsvp_referrer.full_name(),dict['users_rsvp'].pk,dict['users_rsvp'].pk),1).push(request)
		except:
			pass
			# dict['unrsvp_url'] = '/events/%s/unconfirm' % (event_id)
			
		try:
			address = urllib.quote('%sevents/%s' % (our_site, event_id), safe='')
			dict['bitly_address'] = urllib.urlopen('http://api.bit.ly/v3/shorten?login=princetoneventscalendar&apiKey=R_16e331c21bf86e1f97667dec5608dba6&longUrl=%s&format=txt' % address).readlines()[0]
		except:
			dict['bitly_address'] = 'none'
		
		return render_to_response(request,"cal/events_description.html", dict)

	
@login_required
def board_message(request):
	if request.method == 'POST':
		message_title = 'unusued'
		message_body = request.POST.get('message_body',None)
		event_id = request.POST.get('event_id',None)
		user = current_user(request)
		if message_body and event_id and user:
			try:
				myEvent = Event.objects.get(event_id=event_id)
			except:
				return go_back(request,'Malformed message posting. Something is missing',0)
			event_cluster = myEvent.event_cluster
			send_message(user,event_cluster,message_title,message_body).push(request)
			if event_cluster.cluster_user_created != user:
				email_board_message(event_cluster.cluster_user_created, user, myEvent, message_body)
			return HttpResponseRedirect('/events/%s' % event_id)
		else:
			return go_back(request,'Malformed message posting. Something is missing.',0)
	else:
		return go_back(request,'Malformed message posting. You must submit using the proper form.',0)

@login_required
def delete_bmsg(request, bmsg_id):
	try:
		myBMessage = BoardMessage.objects.get(pk = bmsg_id)
		if current_user(request) == myBMessage.boardmessage_poster:
			myBMessage.delete()
			return go_back(request,"You've successfully deleted a message from the discussion board.",1)
		else:
			return go_back(request,"You are not authorized to delete this message.",0)
	except:
		return go_back(request,"I\'m sorry, but that is an illegal action.",0)
		
@login_required
def report_bmsg(request, bmsg_id):
	myBMessage = BoardMessage.objects.get(pk = bmsg_id)
	message = "The following message on PCal was just reported: "
	message = message+str(myBMessage)+"\n\n"
	message = message+"It was posted by: "+myBMessage.getPoster()+" on "+myBMessage.getFormattedTimePosted()+" at "+myBMessage.getTime()+".\n\n"
	message = message+"\nThis is a link to the page where the message was posted:\n\n"
	message = message+our_site
	myCluster = myBMessage.boardmessage_eventcluster
	myEvents = Event.objects.filter(event_cluster = myCluster)
	if myEvents:
		myEvent = myEvents[0]
		myEventUrl = myEvent.get_absolute_url()
		message = message+myEventUrl
	send ("usg@princeton.edu", "usg@princeton.edu", "Princeton Events Calendar: Board Message Reported", message)
	return go_back(request,'A report about this board message was sent to the website administrator. Thank you.',1)

@login_required
def invite(request):
	if request.method == 'POST':
		invitee = request.POST.get('invitee',None)
		event_id = request.POST.get('event_id',None)
		try:
			invitee_u = CalUser.objects.get(user_netid = invitee)
		except:
			if gdi(invitee):
				invitee_u = make_new_user(invitee)
				Msg('%s is new to the calendar, so an account was created.' % (invitee_u.full_name()),1).push(request)
			else:	
				return go_back(request,'The person with netid \'%s\' seems not to exist. Please enter a netid only.' % (cgi.escape(invitee)),0)
		user = current_user(request)
		if invitee_u and event_id and user:
			try:
				event = Event.objects.get(event_id=event_id)
			except:
				return go_back(request,'A corresponding event could not be found.',0)
			send_invite(user,invitee_u,event).push(request)
			return HttpResponseRedirect('/events/%s' % event_id)
		else:
			Msg('Malformed invitation. Something is missing',0).push(request)
		if invitee:
			Msg('Invitee is here.',0).push(request)
		if event_id:
			Msg('Event ID is here.',0).push(request)
		if user:
			Msg('User is here.',0).push(request)
		return go_back(request,'There was a problem.',0)
	else:
		return go_back(request,'Malformed invitation. You must send invitations using the proper form.',0)

@login_required
def invite_response(request,invite_id,action):
	try:
		rsvp = RSVP.objects.get(pk = invite_id)
		if rsvp.rsvp_user != current_user(request):
			return go_back(request,'Operation not permitted by your current user account.',0)
	except:
		return go_back(request,'Illegal operation. That invitation could not be found.',0)
	if action == 'accept':
		accept_invitation(rsvp).push(request)
		return HttpResponseRedirect('/events/%s' % (rsvp.rsvp_event.event_id))
	elif action == 'decline':
		decline_invitation(rsvp).push(request)
		return HttpResponseRedirect('/events/%s' % (rsvp.rsvp_event.event_id))
	else:
		return go_back(request,'Illegal operation.',0)
		
@login_required
def events_forwardtocampusevents(request):
	if request.method == 'POST':
		event_id = request.POST.get('event_id',None)
		custommsg = request.POST.get('message','<No message entered by user>')
		user = current_user(request)
		try:
			event = Event.objects.get(event_id=event_id)
		except:
			return go_back(request,'A corresponding event could not be found.',0)
		if event.isAuthorizedModifier(user):	
			email_forwardtocampusevents(user,event,custommsg)
	 		Msg('Your request was sent successfully',1).push(request)
	 		return HttpResponseRedirect('/events/%s' % (event.event_id))
		else:
			return go_back(request,'You are not authorized to submit this.',0)
	else:
		return go_back(request,'Invalid request.',0)
		
@login_required
def events_add(request):
   user = current_user(request)

   
   EventFormSet = formset_factory(EventForm, formset=RequiredFormSet)
   if request.method == 'POST':
       formset = EventFormSet(request.POST, request.FILES)
       clusterForm = EventClusterForm(request.POST, request.FILES)
       if formset.is_valid() and clusterForm.is_valid():
           new_cluster = clusterForm.save(commit=False)
           new_cluster.cluster_user_created = user
           new_cluster.save()
           clusterForm.save_m2m()
	   
           for form in formset.forms:
               new_event = form.save(commit=False)
               new_event.event_cluster = new_cluster
               new_event.event_user_last_modified = user
               new_event.event_attendee_count = 0
               new_event.save()
               email_creator(user,new_event)

	       # Added for interfacing with Student Groups
           if 'post_groups' in request.POST:
               group = Group.objects.get(id=request.POST['post_groups'])
               entry = Entry(title=new_cluster.cluster_title,text='',event=new_event,group=group)
               entry.save()
               mships = Membership.objects.filter(group=group,feed_notifications=True)
               list = []
               for m in mships:
                   list.append(str(m.student.email))
                   send_mail(EMAIL_HEADER_PREFIX+'\"%s\" Posted to its Feed'%group.name, FEED_NOTIFICATION_EMAIL % (group.name,entry.title,entry.text,group.url), SITE_EMAIL, list, fail_silently=False)

           if 'submit' in request.POST:
              return HttpResponseRedirect('/events/%s?forwardtoevents' % (new_event.event_id))
   else:   
	formset = EventFormSet()
	clusterForm = EventClusterForm()
	try:
		most_recent_submission = Event.objects.filter(event_cluster__cluster_user_created=user).latest('event_cluster__cluster_date_time_created')
		if datetime.now() - most_recent_submission.event_cluster.cluster_date_time_created <= timedelta(minutes=240):
	 		Msg('You just submitted \'<a href="/events/%s">%s</a>\'. Are you adding another date/time for this event or another in this series?<br />Consider adding a <a href="/events/add/%s">related event here</a> instead of a brand new one below.' % (most_recent_submission.pk,most_recent_submission.displayname(),most_recent_submission.pk),2).push(request)
	except:
		pass

   # data for interfacing with Student Groups
   group = None
   group_mships = Membership.objects.filter(student__netid__exact=user.user_netid,type='O')
   if not group_mships.count():
	   try:
		   group = Group.objects.get(netid__exact=user.user_netid)
	   except:
		   pass

   return render_to_response(request, 'cal/events_add.html', {'formset': formset, 'clusterForm': clusterForm, 'group_mships':group_mships, 'group':group})

@login_required
def events_add_another(request, event_id):
   base_event = Event.objects.get(event_id = event_id)
   base_cluster = base_event.event_cluster

   EventFormSet = formset_factory(EventForm, extra=0, formset=RequiredFormSet)
   if request.method == 'POST':
      formset = EventFormSet(request.POST)
      user = request.session.get('user_data',None)
      #eventForm = EventForm(request.POST)
      if formset.is_valid():
         for eventForm in formset.forms:
            new_event = eventForm.save(commit=False)
            new_event.event_cluster = base_cluster
            new_event.event_user_last_modified = user
            new_event.event_attendee_count = 0
            new_event.save()
            email_creator(user,new_event)

         if 'submit' in request.POST:
            #request.session['umessage'] = 'Event just added!'
            return HttpResponseRedirect('/events/%s?forwardtoevents' % (new_event.event_id))
   else:
      #eventForm = EventForm(instance=base_event)
      formset = EventFormSet(initial=[{'event_subtitle': base_event.event_subtitle, 'event_subdescription': base_event.event_subdescription, 'event_date_time_start': base_event.event_date_time_start, 'event_date_time_end': base_event.event_date_time_end, 'event_location': base_event.event_location, 'event_location_details': base_event.event_location_details, 'event_date_rsvp_deadline': base_event.event_date_rsvp_deadline, 'event_max_attendance': base_event.event_max_attendance}])

	#dict = {'cluster': base_cluster, 'eventForm': eventForm }
   return render_to_response(request, 'cal/events_add.html', {'formset':formset, 'event':base_event})

@login_required
def events_manage_ID(request, event_ID):
   thisEvent = Event.objects.get(event_id=event_ID)
   
   if not thisEvent.isAuthorizedModifier(current_user(request)):
      return go_back(request,'Only an event administrator can modify the event.',0)
   
   if Event.objects.filter(event_cluster = thisEvent.event_cluster).count() > 1:
      multiDay = True
   else:
      multiDay = False
      
   if request.method =='POST':
      if 'submit' in request.POST or 'submitnonotify' in request.POST:
         clusterForm = EventClusterForm(request.POST, request.FILES, instance = thisEvent.event_cluster)
         if multiDay:
            eventForm = EventForm(request.POST, instance=thisEvent)
         else:
            eventForm = SingleEventForm(request.POST, instance=thisEvent)
            
         if eventForm.is_valid() and clusterForm.is_valid():
            modifier = current_user(request)
            eF = eventForm.save(commit=False)
            eF.event_user_last_modified = modifier
            eF.save()
            cF = clusterForm.save()
            Msg('The event was successfully updated.',1).push(request)
            if not 'submitnonotify' in request.POST:
				rsvps = RSVP.objects.filter(rsvp_event = eF).filter(rsvp_type = 'Accepted')
				for rsvp in rsvps:
				   user = rsvp.rsvp_user
				   email_event_modification(user, modifier, eF)
				Msg('Number of notification emails sent: %s' % (len(rsvps)),1).push(request)
            else:
				Msg('No attendees were notified.',1).push(request)
            return HttpResponseRedirect('/events/%s' % (eF.event_id))
      elif 'cancel' in request.POST:
          thisEvent.cancelled = True
   else:
      if multiDay:
         eventForm = EventForm(instance=thisEvent)
      else:
         eventForm = SingleEventForm(instance=thisEvent)
      clusterForm = EventClusterForm(instance=thisEvent.event_cluster)
   
   dict = {'eventForm':eventForm, 'clusterForm':clusterForm, 'event':thisEvent}

   return render_to_response(request, 'cal/events_manage.html', dict )

@login_required
def events_cancel(request, event_ID):
   Msg('Canceled events will still remain in the upcoming events list but appear with a strikethrough. Upon cancellation, all attendees will be notified by email.  If you made a mistake that you would like to correct, choose "<a href="/events/manage/%s">Modify this event</a>" instead.<br /><br />Are you sure you wish to cancel this event?<br /><a href="/events/cancel_confirm/%s">Yes, permanently cancel this event.</a> &nbsp;&nbsp;<a href="/events/%s">No, do not cancel ths event.</a>' % (event_ID, event_ID, event_ID),0).push(request)
   return HttpResponseRedirect('/events/%s' % (event_ID))
   
@login_required
def events_cancel_confirm(request, event_ID):
   try:
      event = Event.objects.get(event_id=event_ID)
   except:
      return go_back(request,'Error: Event not found',0)
   modifier = current_user(request)
   if event.isAuthorizedModifier(modifier):	
      event.event_cancelled = True
      event.save()
      rsvps = RSVP.objects.filter(rsvp_event = event).filter(rsvp_type = 'Accepted')
      
      for rsvp in rsvps:
         user = rsvp.rsvp_user
         #if user != modifier:
         email_event_cancellation(user, modifier, event)
      return go_back(request,'This event was permanently cancelled.',1)
   else:
      return go_back(request,'You are not authorized to cancel this event.',0) 

@login_required
def events_delete(request, event_ID):
   Msg('Deleted events will be removed permanently from the calendar system. Upon cancellation, all attendees will be notified by email.  If you made a mistake that you would like to correct, choose "<a href="/events/manage/%s">Modify this event</a>" instead.<br /><br />Are you sure you wish to delete this event?<br /><a href="/events/delete_confirm/%s">Yes, permanently delete this event.</a> &nbsp;&nbsp;<a href="/events/%s">No, do not delete ths event.</a>' % (event_ID, event_ID, event_ID),0).push(request)
   return HttpResponseRedirect('/events/%s' % (event_ID))

@login_required
def events_delete_confirm(request, event_ID):
   try:
      event = Event.objects.get(event_id=event_ID)
   except:
      return go_back(request,'Error: Event not found',0)
   modifier = current_user(request)
   if event.isAuthorizedModifier(modifier):	
      event.event_cancelled = True
      event.event_date_time_start = dtdeleteflag
      event.event_date_time_end = dtdeleteflag
      event.save()
      rsvps = RSVP.objects.filter(rsvp_event = event).filter(rsvp_type = 'Accepted')
      
      for rsvp in rsvps:
         user = rsvp.rsvp_user
         #if user != modifier:
         email_event_cancellation(user, modifier, event)
      return go_back(request,'This event was permanently deleted.',1)
   else:
      return go_back(request,'You are not authorized to delete this event.',0) 


@login_required
def events_search(request):
        dict = {}
	dict['tabtitle'] = "Searched Events"
     	eventsFound = {}
	
	now = datetime.now()
	today = datetime.today()
	today_day = today.day
	today_month = today.month
	today_year = today.year
        midnight = datetime(today.year, today.month, today.day, 0, 0, 0)
        next_week = timedelta(weeks=1)

	fcat = []
	ffeat = []
	timeselect = []

	if 'fcat' in request.GET:
		fcat = request.GET['fcat'].strip()
	if 'ffeat' in request.GET:
		ffeat = request.GET['ffeat'].strip()
	if 'timeselect' in request.GET:
		timeselect = request.GET['timeselect'].strip()

        if 'query' in request.GET:
                query = request.GET['query'].strip()
		 
	        if not query and not fcat and not ffeat and not timeselect:
                #        errorMessage = 'Please enter a search term...here.'
		#	dict={'errorMessage': errorMessage}
		#	return event_processing_dicts(request, eventsFound, dict, template="events_search.html")

			# if no query term, default to returning all future events
			dict['timeselect'] = 'future'	
			dict['default'] = 'yes'
			eventsFound = Event.objects.filter(event_date_time_start__gte=now).order_by('event_date_time_start')
                elif len(query) > 40:
                        errorMessage = 'Please enter at most 40 characters.'
			dict={'errorMessage': errorMessage}
			return event_processing_dicts(request, eventsFound, dict, template="cal/events_search.html")
                else:
			eventsFound = Event.objects.exclude(event_date_time_start=dtdeleteflag).all().order_by('event_date_time_start')
			q = Q()

			keywords = query.split()
			for keyword in keywords:
				q = q | Q(event_cluster__cluster_title__icontains=keyword) | Q(event_subtitle__icontains=keyword)
				q = q | Q(event_cluster__cluster_description__icontains=keyword) | Q(event_subdescription__icontains=keyword)          
				
			if ('fcat' in request.GET):
				category_query = request.GET['fcat']
				if category_query and category_query != 'cat_all':			
					category = EventCategory.objects.get(category_name=category_query)
					Msg("Filtering only by category: '%s'" % (category),1).push(request)
					q = q & Q(event_cluster__cluster_category=category)
				else:
					category = 'cat_all'
			else:
				category = 'cat_all'

			if ('ffeat' in request.GET):
				feature_query = request.GET['ffeat']
				if feature_query and feature_query != 'feat_all':
					feature = EventFeature.objects.get(feature_name=feature_query)
					Msg("Filtering only by feature: '%s'" % (feature),1).push(request)
					q = q & Q(event_cluster__cluster_features=feature)
				else:
					feature = 'feat_all'
			else:
				feature = 'feat_all'
			eventsFound = Event.objects.exclude(event_date_time_start=dtdeleteflag).filter(q).order_by('event_date_time_start')

			if 'timeselect' in request.GET:
				timeselect = request.GET['timeselect'].strip()
				if timeselect == 'today':
					q = q & Q(event_date_time_start__day=today_day,event_date_time_start__month=today_month, event_date_time_start__year=today_year)
					eventsFound = Event.objects.filter(q).order_by('event_date_time_start')
					
				elif timeselect == 'week':
					q = q & Q(event_date_time_start__gte=midnight,event_date_time_start__lte=midnight + next_week)
					eventsFound = Event.objects.filter(q).order_by('event_date_time_start')
				elif timeselect == 'weekend':
					q = q & Q(event_date_time_start__gte=midnight) & Q(event_date_time_start__lte=midnight + next_week) & (Q(event_date_time_start__week_day=1) | Q(event_date_time_start__week_day=6) | Q(event_date_time_start__week_day=7))
					eventsFound = Event.objects.filter(q).order_by('event_date_time_start')
				elif timeselect == 'past':
					q = q & Q(event_date_time_start__lte=now)
					eventsFound = Event.objects.exclude(event_date_time_start=dtdeleteflag).filter(q).order_by('event_date_time_start')
				elif timeselect == 'all':
					eventsFound = Event.objects.exclude(event_date_time_start=dtdeleteflag).filter(q).order_by('event_date_time_start')
				else:
					timeselect = 'future'
					q = q & Q(event_date_time_start__gte=now)
					eventsFound = Event.objects.filter(q).order_by('event_date_time_start')
				
			# have default be show only future events.
			else:
				timeselect = 'future'
				q = q & Q(event_date_time_start__gte=now)
				eventsFound = Event.objects.filter(q).order_by('event_date_time_start')

			dict={'query':query, 'keywords':keywords, 'timeselect': timeselect, 'feature':feature, 'category':category}
			return event_processing_dicts(request, eventsFound, dict, template="cal/events_search.html")

	# if no query term, default to returning all future events
	dict['timeselect'] = 'future'	
	dict['default'] = 'yes'
	eventsFound = Event.objects.filter(event_date_time_start__gte=now).order_by('event_date_time_start')
	return event_processing_dicts(request, eventsFound, dict, template="cal/events_search.html")
	
@login_required
def showQR(request, event_id):
	try:
		myEvent = Event.objects.get(event_id=event_id)
	except:
		return go_back(request, 'Error: No event found',0)
	user = current_user(request)
	dict = {'event': myEvent}
	dict['tabtitle'] = 'Quick Response Code'
	dict['user'] = user
	dict['personal_link'] = '%sbulkinvite/%s-%s-p' % (our_site, myEvent.pk, user.pk)
	personallongencoded = urllib.urlencode({'login':'princetoneventscalendar',
											'apiKey':'R_16e331c21bf86e1f97667dec5608dba6',
											'longUrl':dict['personal_link'],
											'format':'txt',})
	bitlylink = 'http://api.bit.ly/v3/shorten?%s' % (personallongencoded)
	dict['personalqr_link'] = urllib.urlopen(bitlylink).readlines()[0]
	personalqrparams = urllib.urlencode({	's':'8',
											't':'p',
											'd':dict['personalqr_link'],})
	dict['personalqr_url'] = 'http://qrcode.kaywa.com/img.php?%s' % (personalqrparams)
	dict['generalqr_link'] = '%sevents/%s' % (our_site, myEvent.pk)
	generalqrparams = urllib.urlencode({	's':'8',
											't':'p',
											'd':dict['generalqr_link'],})
	dict['generalqr_url'] = 'http://qrcode.kaywa.com/img.php?%s' % (generalqrparams)
	return render_to_response(request,"cal/qr_code.html", dict)
	
@login_required	
def custom_invite_message(request, event_id):
	try:
		myEvent = Event.objects.get(event_id=event_id)
	except:
		return go_back(request, 'Error: No event found',0)
	user = current_user(request)
	if not myEvent.isAuthorizedModifier(user):
		Msg('Only an event administrator can use this feature to send invitations to a list.',0).push(request)
		return HttpResponseRedirect('/events/%s' % event_id)
	else:
		dict = {'event': myEvent}
		dict['flag_custom_invite'] = True
		return render_to_response(request,"cal/email_attendees.html", dict)

@login_required	
def custom_invite_message_sent(request, event_id):
	if request.method == 'POST':
		myEvent = Event.objects.get(event_id=event_id)
		user = current_user(request)
		if not myEvent.isAuthorizedModifier(user):
			return go_back(request, 'You are not authorized to complete this action.',0)
		message_from = request.POST.get('from',None)
		if not message_from:
			return go_back(request, 'You must provide a valid "from" address.',0)
		message_to = request.POST.get('to',None)
		if not message_to:
			return go_back(request, 'You must provide a valid "to" address.',0)
		message_title = request.POST.get('subject',None)
		message_body = request.POST.get('message',None)
		return email_custom_invitation(request, myEvent, message_from, message_to, message_title, message_body)
	else:
		return go_back(request, 'Invalid request.',0)	

@login_required
def bulk_invite_response(request, event_id, sender_id, response):
	try:
		event = Event.objects.get(pk = event_id)
	except:
		return go_back(request, 'Invalid event number.',0)
	try:
		inviter = CalUser.objects.get(pk = sender_id)
	except:
		return go_back(request, 'Invalid user.',0)
	user = current_user(request)
	try:
		existing_rsvp = RSVP.objects.get(rsvp_user=user, rsvp_event=event)
		if existing_rsvp.rsvp_type == 'Accepted':
			if response == 'a':
				Msg('You have already confirmed your attendance for this event.',0).push(request)
			elif response == 'd':
				decline_invitation(existing_rsvp).push(request)
			else:
				pass
		elif existing_rsvp.rsvp_type == 'Pending':
			if response == 'a':
				accept_invitation(existing_rsvp).push(request)
			elif response == 'd':
				decline_invitation(existing_rsvp).push(request)
			else:
				pass		
		else:
			if response == 'a':
				Msg('You have already declined attendance for this event. Would you like to <a href="/user/invitations/%s/accept/">change your mind</a>?' % (existing_rsvp.pk),0).push(request)				
			elif response == 'd':
				Msg('You have already declined attendance for this event.',0).push(request)				
			else:
				pass
	except:
		rsvp = RSVP(rsvp_user = current_user(request),
					rsvp_referrer = inviter,
					rsvp_event = event,
					rsvp_reminder_enabled = True,
					rsvp_type='Pending')
		rsvp.save()
		if response == 'a':
			accept_invitation(rsvp).push(request)	
		elif response == 'd':
			decline_invitation(rsvp).push(request)
		elif response == 'p':
			return HttpResponseRedirect('/events/%s?showrsvp=true' % event_id)
		else:
			return go_back(request, 'Invalid status.',0)
	return HttpResponseRedirect('/events/%s' % event_id)

	
@login_required
def ical(request, event_id):
   event = Event.objects.get(event_id=event_id)
   cal = vobject.iCalendar()
   cal.add('method').value = 'PUBLISH'  # IE/Outlook needs this
   
   vevent = cal.add('vevent')
   vevent.add('summary').value = str(event)
   vevent.add('dtstart').value = event.event_date_time_start
   vevent.add('dtend').value = event.event_date_time_end

   vevent.add('location').value = event.getGCalLocation()
   vevent.add('description').value = event.getGCalClusterDes() + "\n\n" + event.getGCalEventDes()

   icalstream = cal.serialize()
   response = HttpResponse(icalstream, mimetype='text/calendar')
   response['Filename'] = 'pcal.ics'  # IE needs this
   response['Content-Disposition'] = 'attachment; filename=pcal.ics'
   return response


#Feeds
def feedLanding(request, name, description):
	dict = {}
	dict['http_feed_continue'] = request.build_absolute_uri()
	dict['webcal_feed_continue'] = request.build_absolute_uri().replace('http://','webcal://')
	dict['tabtitle'] = 'Live Feed: \'%s\'' % (name)
	dict['feed_name'] = name
	dict['feed_desc'] = description
	return render_to_response(request,"cal/feed_landing.html", dict)

def feedRedirect(request):
	#Msg('ct: %s' % request.build_absolute_uri(),0).push(request)
	if request.build_absolute_uri().find('webcal://') == 0:
		return False
	ref = request.META.get('HTTP_REFERER',None)
	#Msg('Ref: %s' % ref,0).push(request)
	
	if ref and ref.find(our_site) == 0:
		ref_path = ref.replace(our_site,'/')
		#Msg('Ref_path: %s' % ref_path,0).push(request)
		cur = request.path
		#Msg('cur: %s' % cur,0).push(request)
		if ref_path != cur:
			return True
		else:
			return False
	else:
		return False
	

def feedByCategory(request, category):
	try:
		filter_cat = EventCategory.objects.get(category_name=category)
	except:
		return go_back(request, 'Invalid category.',0)
	name = "'%s' Events" % (category);
	description = "Live Feed: Events in the category '%s' posted on the Princeton Events Calendar, a service of the Princeton USG. For the full calendar, visit %s." % (category, our_site);
	if feedRedirect(request):
		return feedLanding(request, name, description)
	events = Event.objects.exclude(event_date_time_start=dtdeleteflag).filter(event_cluster__cluster_category=filter_cat)
	return generateFeed(events, name, description)
	
def feedByFeature(request, feature):
	try:
		filter_feat = EventFeature.objects.get(feature_name=feature)
	except:
		return go_back(request, 'Invalid feature.',0)
	name = "'%s' Events" % (feature);
	description = "Live Feed: Events featuring '%s' posted on the Princeton Events Calendar, a service of the Princeton USG. For the full calendar, visit %s." % (feature, our_site);
	if feedRedirect(request):
		return feedLanding(request, name, description)
	events = Event.objects.exclude(event_date_time_start=dtdeleteflag).filter(event_cluster__cluster_features=filter_feat)
	return generateFeed(events, name, description)	
	
def feedByUser(request, user):
	try:
		filter_user = CalUser.objects.get(user_netid=user)
	except:
		return go_back(request, 'Invalid user.',0)
	name = "Events by %s" % (filter_user.full_name_suffix());
	description = "Live Feed: Events posted by '%s' to the Princeton Events Calendar, a service of the Princeton USG. For the full calendar, visit %s." % (filter_user.full_name_suffix(), our_site);
	if feedRedirect(request):
		return feedLanding(request, name, description)
	events = Event.objects.exclude(event_date_time_start=dtdeleteflag).filter(event_cluster__cluster_user_created=filter_user)
	return generateFeed(events, name, description)		

def feedAllEvents(request):
	name = "All Campus Events"
	description = "Live Feed: All upcoming events posted to the Princeton Events Calendar, a service of the Princeton USG. For the full calendar, visit %s." % our_site
	if feedRedirect(request):
		return feedLanding(request, name, description)
	events = Event.objects.exclude(event_date_time_start=dtdeleteflag).filter(event_date_time_start__gte=datetime.now())
	return generateFeed(events, name, description)
	
def feedMyEvents(request, id, netid):
	user = CalUser.objects.get(pk=id)
	check = CalUser.objects.get(user_netid=netid)
	
	if user != check:
		return go_back(request, 'Malformed link.',0)
		
	name = 'My Campus Events'
	description = "Live Feed: %s's personal events on the Princeton Events Calendar. Includes events to which you confirmed attendance for synchronizing with your personal calendar program. Set your calendar program to synchronize this feed at least hourly for best accuracy. Keep this link private. For the full calendar, visit %s." % (user.full_name(), our_site)
	if feedRedirect(request):
		return feedLanding(request, name, description)
	rsvps = RSVP.objects.exclude(rsvp_event__event_date_time_start=dtdeleteflag).filter(rsvp_user=user,rsvp_type='Accepted')
	events = []
	for rsvp in rsvps:
		events.append(rsvp.rsvp_event)
	return generateFeed(events, name, description)

def generateFeed(events, name, description):
	cal = vobject.iCalendar()
	cal.add('CALSCALE').value = 'GREGORIAN'
	cal.add('METHOD').value = 'PUBLISH'
	cal.add('X-WR-CALNAME').value = name
	cal.add('X-WR-TIMEZONE').value = 'America/New_York'
	cal.add('X-WR-CALDESC').value = description
	
	for event in events:
		vevent = cal.add('VEVENT')
		vevent.add('UID').value = "%i@%s" % (event.event_id, our_email)
		vevent.add('RELATED-TO').value = 'RELTYPE=CHILD:%irecur@%s' % (event.event_cluster.cluster_id, our_email)
		vevent.add('SUMMARY').value = smart_unicode(str(event))
		vevent.add('DTSTART').value = event.event_date_time_start
		vevent.add('DTEND').value = event.event_date_time_end
		vevent.add('CREATED').value = event.event_cluster.cluster_date_time_created
		vevent.add('LAST-MODIFIED').value = event.event_date_time_last_modified
		if event.event_cancelled == True:
			vevent.add('STATUS').value = "CANCELLED"
		else:
			vevent.add('STATUS').value = "CONFIRMED"
		vevent.add('URL').value = event.get_absolute_url()
		vevent.add('TRANSP').value = 'TRANSPARENT'
		vevent.add('ORGANIZER').value = '%s' % (event.event_cluster.cluster_user_created.user_email)
		
		vevent.add('LOCATION').value = unicode(event.getGCalLocation())
		vevent.add('DESCRIPTION').value = unicode(event.getGCalClusterDes() + "\n\n" + event.getGCalEventDes())

	icalstream = cal.serialize()
	response = HttpResponse(icalstream, mimetype='text/calendar')
	response['Content-Type'] = 'text/calendar; charset=utf-8'
# 	response['Transfer-Encoding'] = 'chunked'
	response['Connection'] = 'close'
	response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
	response['Pragma'] = 'no-cache'
	return response	

def icalFeed(request, category):
	cal = vobject.iCalendar()
	cal.add('CALSCALE').value = 'GREGORIAN'
	cal.add('METHOD').value = 'PUBLISH'
	cal.add('X-WR-CALNAME').value = category + ' Events'
	cal.add('X-WR-TIMEZONE').value = 'America/New_York'
	cal.add('X-WR-CALDESC').value = 'Calendar of campus events. Filter:'+category
	
	filteredEvents = Event.objects.filter(event_date_time_end__lte=datetime.now()).order_by('event_date_time_start')
	if not category == "All":
		filteredEvents = filteredEvents.filter(event_cluster__cluster_category__category_name=category)
	
	for event in filteredEvents[0:200]:
		vevent = cal.add('VEVENT')
		vevent.add('SUMMARY').value = smart_unicode(str(event))
		vevent.add('DTSTART').value = event.event_date_time_start
		vevent.add('DTEND').value = event.event_date_time_end
		
		vevent.add('LOCATION').value = unicode(event.getGCalLocation())
		vevent.add('DESCRIPTION').value = unicode(event.getGCalClusterDes() + "\n\n" + event.getGCalEventDes())

	icalstream = cal.serialize()
	response = HttpResponse(icalstream, mimetype='text/calendar')
	response['Content-Type'] = 'text/calendar; charset=utf-8'
# 	response['Transfer-Encoding'] = 'chunked'
	response['Connection'] = 'close'
	response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
	response['Pragma'] = 'no-cache'
	return response

def subscribe(request, category):
	cal = vobject.iCalendar()
	cal.add('CALSCALE').value = 'GREGORIAN'
	cal.add('METHOD').value = 'PUBLISH'
	cal.add('X-WR-CALNAME').value = category + ' Events'
	cal.add('X-WR-TIMEZONE').value = 'America/New_York'
	cal.add('X-WR-CALDESC').value = 'Calendar of campus events. Filter:'+category
	cal.add('X-PUBLISHED-TTL').value = 'PT60M'
	
	filteredEvents = Event.objects.order_by('event_date_time_start')
	if not category == "All":
		filteredEvents = filteredEvents.filter(event_cluster__cluster_category__category_name=category)

	for event in filteredEvents:
		vevent = cal.add('VEVENT')
		vevent.add('UID').value = "%i@%s" % (event.event_id, our_email)
		vevent.add('RELATED-TO').value = 'RELTYPE=CHILD:%irecur@%s' % (event.event_cluster.cluster_id, our_email)
		vevent.add('SUMMARY').value = smart_unicode(str(event))
		vevent.add('DTSTART').value = event.event_date_time_start
		vevent.add('DTEND').value = event.event_date_time_end
		vevent.add('CREATED').value = event.event_cluster.cluster_date_time_created
		vevent.add('LAST-MODIFIED').value = event.event_date_time_last_modified
		if event.event_cancelled == True:
			vevent.add('STATUS').value = "CANCELLED"
		else:
			vevent.add('STATUS').value = "CONFIRMED"
		vevent.add('URL').value = event.get_absolute_url()
		vevent.add('TRANSP').value = 'TRANSPARENT'
		vevent.add('ORGANIZER').value = '%s' % (event.event_cluster.cluster_user_created.user_email)
		
		vevent.add('LOCATION').value = unicode(event.getGCalLocation())
		vevent.add('DESCRIPTION').value = unicode(event.getGCalClusterDes() + "\n\n" + event.getGCalEventDes())
		


	icalstream = cal.serialize()
	response = HttpResponse(icalstream, mimetype='text/calendar')
	response['Content-Type'] = 'text/calendar; charset=utf-8'
	response['Connection'] = 'close'
	response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
	response['Pragma'] = 'no-cache'
	return response

def personalCalendar(request, id, netid):
	user = CalUser.objects.get(pk=id)
	check = CalUser.objects.get(user_netid=netid)
	
	if user != check:
		return
	
	cal = vobject.iCalendar()
	cal.add('CALSCALE').value = 'GREGORIAN'
	cal.add('METHOD').value = 'PUBLISH'
	cal.add('X-WR-CALNAME').value = 'My Campus Events'
	cal.add('X-WR-TIMEZONE').value = 'America/New_York'
	cal.add('X-WR-CALDESC').value = '%s\'s personal events from the Princeton Events Calendar, %s.' % (user.full_name(), our_site)
	cal.add('X-PUBLISHED-TTL').value = 'PT1H'
	
	
	userRSVPs = RSVP.objects.filter(rsvp_user=user,rsvp_type='Accepted').order_by('rsvp_event__event_date_time_start')

	for rsvp in userRSVPs:
		event = rsvp.rsvp_event
		vevent = cal.add('VEVENT')
		vevent.add('UID').value = "%i@%s" % (event.event_id, our_email)
		vevent.add('RELATED-TO').value = 'RELTYPE=CHILD:%irecur@%s' % (event.event_cluster.cluster_id, our_email)
		vevent.add('SUMMARY').value = smart_unicode(str(event))
		vevent.add('DTSTART').value = event.event_date_time_start
		vevent.add('DTEND').value = event.event_date_time_end
		vevent.add('CREATED').value = event.event_cluster.cluster_date_time_created
		vevent.add('LAST-MODIFIED').value = event.event_date_time_last_modified
		if event.event_cancelled == True:
			vevent.add('STATUS').value = "CANCELLED"
		else:
			vevent.add('STATUS').value = "CONFIRMED"
		vevent.add('URL').value = event.get_absolute_url()
		vevent.add('TRANSP').value = 'TRANSPARENT'
		vevent.add('ORGANIZER').value = '%s' % (event.event_cluster.cluster_user_created.user_email)
		
		vevent.add('LOCATION').value = unicode(event.getGCalLocation())
		vevent.add('DESCRIPTION').value = unicode(event.getGCalClusterDes() + "\n\n" + event.getGCalEventDes())
		


	icalstream = cal.serialize()
	response = HttpResponse(icalstream, mimetype='text/calendar')
	response['Content-Type'] = 'text/calendar; charset=utf-8'
	response['Connection'] = 'close'
	response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
	response['Pragma'] = 'no-cache'
	return response
	
def followCalendar(request, netid):
	user = CalUser.objects.get(user_netid=netid)
	
	cal = vobject.iCalendar()
	cal.add('CALSCALE').value = 'GREGORIAN'
	cal.add('METHOD').value = 'PUBLISH'
	cal.add('X-WR-CALNAME').value = '%s Events' % user.full_name()
	cal.add('X-WR-TIMEZONE').value = 'America/New_York'
	cal.add('X-WR-CALDESC').value = 'Events submitted by %s to the Princeton Events Calendar, %s.' % (user.full_name(), our_site)
	cal.add('X-PUBLISHED-TTL').value = 'PT1H'
	
	publishedEvents = Event.objects.filter(event_cluster__cluster_user_created=user).order_by('event_date_time_start')

	for event in publishedEvents:
		vevent = cal.add('VEVENT')
		vevent.add('UID').value = "%i@%s" % (event.event_id, our_email)
		vevent.add('RELATED-TO').value = 'RELTYPE=CHILD:%irecur@%s.' % (event.event_cluster.cluster_id, our_email)
		vevent.add('SUMMARY').value = smart_unicode(str(event))
		vevent.add('DTSTART').value = event.event_date_time_start
		vevent.add('DTEND').value = event.event_date_time_end
		vevent.add('CREATED').value = event.event_cluster.cluster_date_time_created
		vevent.add('LAST-MODIFIED').value = event.event_date_time_last_modified
		if event.event_cancelled == True:
			vevent.add('STATUS').value = "CANCELLED"
		else:
			vevent.add('STATUS').value = "CONFIRMED"
		vevent.add('URL').value = event.get_absolute_url()
		vevent.add('TRANSP').value = 'TRANSPARENT'
		vevent.add('ORGANIZER').value = '%s' % (event.event_cluster.cluster_user_created.user_email)
		
		vevent.add('LOCATION').value = unicode(event.getGCalLocation())
		vevent.add('DESCRIPTION').value = unicode(event.getGCalClusterDes() + "\n\n" + event.getGCalEventDes())

	icalstream = cal.serialize()
	response = HttpResponse(icalstream, mimetype='text/calendar')
	response['Content-Type'] = 'text/calendar; charset=utf-8'
	response['Connection'] = 'close'
	response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
	response['Pragma'] = 'no-cache'
	return response
	

def go_back(request, error_msg = None, type = 0):
	if error_msg:
		Msg(error_msg,type).push(request)
	ref = request.META.get('HTTP_REFERER',None)
	if ref and ref.find(our_site) == 0:
		ref = ref.replace(our_site,'/',1)
	else:
		ref = '/'
	return HttpResponseRedirect(ref)	
		
def xml_feed(request):
    now = datetime.now()
    if 'from' in request.GET and 'to' in request.GET:
        from_time = request.GET['from']
        to_time = request.GET['to']
        from_split = from_time.split("-", 2)
        from_date = datetime(int(from_split[0]), int(from_split[1]), int(from_split[2]), 0, 0, 0)
        to_split = to_time.split("-", 2)
        to_date = datetime(int(to_split[0]), int(to_split[1]), int(to_split[2]), 23, 59, 59)
        eventList = Event.objects.filter(event_date_time_end__gte=from_date).filter(event_date_time_end__lte=to_date).order_by('event_date_time_start')
    else:
        eventList = Event.objects.filter(event_date_time_end__gte=datetime.now()).order_by('event_date_time_start')
        
    t = loader.get_template("cal/xml_feed.html")
    c = Context({'eventList': eventList, 'now': now})
    return HttpResponse(t.render(c),
            mimetype="text/xml")
