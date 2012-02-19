################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  views_users.py
# Info :  rendering user pages (profile, personal events, etc.)
################################################################

from django.http import *
from render import render_to_response
from django.contrib.auth import login
import urllib, re, datetime
from models import *
from cauth import *
from rsvp import *
from forms import *
from views_events import *
from decorators import login_required
from datetime import datetime, timedelta

@login_required
def activityFeed(request):
	user = current_user(request)
	if user.user_netid not in SITE_ADMINS:
		return HttpResponseRedirect('/')
	
	cutoff = datetime.now() - timedelta(hours = 48)
	
	feedItems = []
	
	userLogins = CalUser.objects.filter(user_last_login__gte=cutoff)
	for ul in userLogins:
		feedItems.append((ul.user_last_login,'%s: %s logged in' % (ul.user_last_login.strftime("%d/%m/%y %I:%M%p"),ul.full_name_suffix())))
	
	clusterCreated = EventCluster.objects.filter(cluster_date_time_created__gte=cutoff)
	for cc in clusterCreated:
		feedItems.append((cc.cluster_date_time_created,'%s: %s created event cluster \'%s\'' % (cc.cluster_date_time_created.strftime("%d/%m/%y %I:%M%p"),cc.cluster_user_created.full_name_suffix(), cc.cluster_title)))
	
	bMessages = BoardMessage.objects.filter(boardmessage_time_posted__gte = cutoff)
	for bm in bMessages:
		feedItems.append((bm.boardmessage_time_posted,'%s: %s posted a message to event cluster \'%s\'' % (bm.boardmessage_time_posted.strftime("%d/%m/%y %I:%M%p"),bm.boardmessage_poster.full_name_suffix(), bm.boardmessage_eventcluster.cluster_title)))
		
	rsvps = RSVP.objects.filter(rsvp_date_created__gte=cutoff)
	for rsvp in rsvps:
		if rsvp.rsvp_referrer:
			feedItems.append((rsvp.rsvp_date_created,'%s: %s has a %s RSVP to event \'%s\' from %s' % (rsvp.rsvp_date_created.strftime("%d/%m/%y %I:%M%p"),rsvp.rsvp_user.full_name_suffix(), rsvp.rsvp_type, rsvp.rsvp_event.displayname(), rsvp.rsvp_referrer.full_name_suffix())))		
		else:
			feedItems.append((rsvp.rsvp_date_created,'%s: %s has a %s RSVP to event \'%s\'' % (rsvp.rsvp_date_created.strftime("%d/%m/%y %I:%M%p"),rsvp.rsvp_user.full_name_suffix(), rsvp.rsvp_type, rsvp.rsvp_event.displayname())))		
	
	views = View.objects.filter(view_date_time__gte=cutoff)
	for v in views:
		feedItems.append((v.view_date_time,'%s: %s viewed \'%s\' for the %s time' % (v.view_date_time.strftime("%d/%m/%y %I:%M%p"),v.view_viewer.full_name_suffix(), v.view_event.displayname(),v.view_count)))
		
	
	feedItems = sorted(feedItems, key=lambda item: item[0], reverse=True)
	
	dict = {}
	dict['happenings'] = feedItems
	
	return render_to_response(request, 'cal/easteregg.html', dict)
	

@login_required
def user_profile(request):
   try:
      if request.method =='POST':
         profileForm = EditUserForm(request.POST, instance=request.session['user_data'])
         if profileForm.is_valid():
            user = profileForm.save()
            request.session['user_data']=user
            Msg("Profile successfully updated", 1).push(request)
         if 'newbie' in request.GET:
            if 'login_redirect' in request.session:
               referrer = request.session['login_redirect']
               del request.session['login_redirect']
               return HttpResponseRedirect(referrer)
            else:
               return HttpResponseRedirect('/')
         
      else:
         profileForm = EditUserForm(instance=request.session['user_data'])
   
      dict = {'profileForm':profileForm}

   except KeyError:
      dict = {}
   
   return render_to_response(request, 'cal/user_profile.html', dict )

@login_required
def user_events(request, events_array, dict):
#                 all_my_events = [] 
#                 for all_rsvp in events_array: 
#                    all_my_events.append(all_rsvp.rsvp_event) 
#                 my_dates = [] 
#                 events_on_date = {}
#                 for event in all_my_events: 
#                    date_string = event.event_date_time_start.strftime("%A, %B %e") 
#                    if date_string not in my_dates: 
#                       my_dates.append(date_string)
#                       events_on_date[date_string] = [] 
#                    events_on_date[date_string].append(event) 
#                                                                                
#                 dict['all_my_dates'] = my_dates 
#                 dict['events_on_date'] = events_on_date       
	my_dates = []
	events_on_date = {}
	for rsvp in events_array:
		date_string = rsvp.rsvp_event.event_date_time_start.strftime("%A, %B %e")
		if date_string not in my_dates:
			my_dates.append(date_string)
			events_on_date[date_string] = []
		events_on_date[date_string].append((rsvp.rsvp_event,rsvp))

	dict['all_my_dates'] = my_dates
	dict['events_on_date'] = events_on_date
	dict['feat_opts'] = EventFeature.objects.all()  
	return render_to_response(request, 'cal/myevents.html', dict)                

@login_required
def user_upcoming_events(request):
   dict ={}
   user = current_user(request)
   dict['show_prev'] = 'true'
   dict['tabtitle'] = "%s's Upcoming Events" % (user.user_firstname)
   dict['feat_opts'] = EventFeature.objects.all()  
   dict['feedurl'] = '%smycal/%s/%s.ics' % (our_site, user.pk, user.user_netid)
   all_my_RSVP = RSVP.objects.exclude(rsvp_event__event_date_time_start=dtdeleteflag).filter(rsvp_user=current_user(request),rsvp_type='Accepted',rsvp_event__event_date_time_start__gte=datetime.now()).order_by('rsvp_event__event_date_time_start')
   return user_events(request, all_my_RSVP, dict)

@login_required
def user_past_events(request):
   user = current_user(request)
   dict = {}
   dict['tabtitle'] = "%s's Past Events" % (user.user_firstname)
   dict['feat_opts'] = EventFeature.objects.all()  
   all_my_RSVP = RSVP.objects.exclude(rsvp_event__event_date_time_start=dtdeleteflag).filter(rsvp_user=current_user(request),rsvp_type='Accepted',rsvp_event__event_date_time_start__lte=datetime.now()).order_by('rsvp_event__event_date_time_start')
   return user_events(request, all_my_RSVP, dict)

@login_required
def user_admin_events(request):
	user = current_user(request)
	dict = {}
	dict['tabtitle'] = "%s's Created Events" % (user.user_firstname)
	array = Event.objects.exclude(event_date_time_start=dtdeleteflag).filter(event_cluster__cluster_user_created=current_user(request)).order_by('event_date_time_start')
	my_dates = []
	events_on_date = {}
	usr = current_user(request)
	for event in array:
		date_string = event.event_date_time_start.strftime("%A, %B %e")
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
	dict['feat_opts'] = EventFeature.objects.all()  
	return render_to_response(request, 'cal/myevents.html', dict)
   
@login_required
def user_invitations(request):
	dict = {}
	user = current_user(request)
	dict['pending_invites'] = RSVP.objects.filter(rsvp_user=user,rsvp_event__event_date_time_start__gte=datetime.now(),rsvp_type='Pending').order_by('rsvp_event__event_date_time_start')
	dict['accepted_invites'] = RSVP.objects.filter(rsvp_user=user,rsvp_type='Accepted',rsvp_referrer__isnull=False, rsvp_event__event_date_time_start__gte=datetime.now()).order_by('rsvp_event__event_date_time_start')
	dict['declined_invites'] = RSVP.objects.filter(rsvp_user=user,rsvp_type='Declined', rsvp_event__event_date_time_start__gte=datetime.now() ).order_by('rsvp_event__event_date_time_start')
	return render_to_response(request, 'cal/myinvites.html', dict)     

@login_required
def user_messages(request):
	dict = {}
	user = current_user(request)
	all_messages = UserMessage.objects.filter(um_user = user).order_by('um_date_posted').reverse()
	dict['unread_messages'] = UserMessage.objects.filter(um_user = user, um_date_read = None).order_by('um_date_posted').reverse()
	len(dict['unread_messages']) #Evaluate it now!
	dict['read_messages'] = UserMessage.objects.filter(um_user = user).exclude(um_date_read = None).order_by('um_date_posted').reverse()[0:5]
 	len(dict['read_messages']) #Evaluate it now!
	for msg in dict['unread_messages']:
	 	msg.mark_read()
	return render_to_response(request, 'cal/user_messages.html', dict)

def user_messages_hover(request):
	dict = {}
	user = current_user(request)
	dict['unread_messages'] = UserMessage.objects.filter(um_user = user, um_date_read = None).order_by('um_date_posted').reverse()
	Msg('You just loaded a tooltip!',1).push(request)
	return render_to_response(request, 'cal/hover_messages.html', dict)

def nocookie(request):
	dict = {}
	return render_to_response(request, 'cal/nocookie.html', dict)

def userlookup(request):
	if request.method == 'GET' and 'netid' in request.GET:
		netid = request.GET.get('netid',None);
		results = gdi(netid)
		dn = results['displayName']
		return HttpResponse(dn); 
	else:
		return HttpResponse('<html><body>Invalid request</body></html>'); 
		



@login_required
def user_alerts(request):
        html = '<html><body>This is the %s page</body></html>' % (request.get_full_path())
        return HttpResponse(html);