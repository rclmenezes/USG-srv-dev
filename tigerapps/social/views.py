from social.models import *
from ttrade.search import get_query
from dsml import gdi
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseForbidden
from datetime import datetime, timedelta, date
from django.shortcuts import get_object_or_404, render_to_response
import json

def check_undergraduate(username):
    # Check if user can be here
    try:
        user = SocUser.objects.get(netid=username)
    except:
        info = gdi(username)
        user = SocUser(netid=username, firstname=info.get('givenName'), lastname=info.get('sn'), pustatus=info.get('pustatus'))
        if info.get('puclassyear'):
            user.puclassyear = int(info.get('puclassyear'))
        user.save()
        
    if user.pustatus == 'undergraduate' and 2011 < user.puclassyear:
        return True
    return False
    
@login_required  
def search(request):
    # Check if user can be here
    if not check_undergraduate(request.user.username):# or not request.is_ajax():
        return HttpResponseForbidden()
        
    if 'search' in request.GET:
        query = request.GET['search']
        if query != "" and query.strip() != "": 
            event_list = Event.objects.filter(get_query(query, ['title', 'description', 'club__name'])).order_by('-time_start')
            
            return render_to_response('social/search.html', {'event_list': event_list})
        
    return HttpResponseForbidden()

@login_required  
def night(request, month, day, year):
    # Check if user can be here
    if not check_undergraduate(request.user.username):
        return HttpResponseForbidden()
    
    # Initialize club list
    clubs = Club.objects.all()
    club_list = {}
    for club in clubs:
        club_list[club.slug] = (club, [],)
        
    # Get events
    target_day = date(month=int(month), day=int(day), year=int(year))
    next_day = target_day + timedelta(days=1)
    prev_day = target_day - timedelta(days=1)
    event_list = Event.objects.filter(time_start__gt=target_day, time_start__lt=next_day)
    
    # Load events into club_list
    for event in event_list:
        club_list[event.club.slug][1].append(event)
    
    if target_day.weekday() != 6:
        week_start = target_day - timedelta(days=target_day.weekday() + 1)
    else:
        week_start = target_day

    days = []
    for i in range(0,7):
        if target_day.weekday() == i-1 or (target_day.weekday() == 6 and i == 0):
            days.append((week_start + timedelta(days=i), True))
        else:
            days.append((week_start + timedelta(days=i), False))
    
    next_week = target_day + timedelta(days=7)
    prev_week = target_day - timedelta(days=7)
    
    return render_to_response('social/base.html', {'club_list': club_list, 'next_week': next_week, 'prev_week': prev_week, 'days': days})

# See description and picture and picture
# If officer, see edit description and add event
@login_required  
def club(request, club):
    # Check if user can be here
    if not check_undergraduate(request.user.username):
        return HttpResponseForbidden()
    
    club = Club.objects.get(slug=club)
    return HttpResponse(club.name + "<br/>" + club.about)
    
@login_required  
def event(request, event_id):
    # Check if user can be here
    if not check_undergraduate(request.user.username):
        return HttpResponseForbidden()
        
    days = []
    target_day = datetime.now()
    if target_day.weekday() != 6:
        week_start = target_day - timedelta(days=target_day.weekday() + 1)
    else:
        week_start = target_day
    for i in range(0,7):
        if target_day.weekday() == i-1 or (target_day.weekday() == 6 and i == 0):
            days.append((week_start + timedelta(days=i), True))
        else:
            days.append((week_start + timedelta(days=i), False))

    next_week = target_day + timedelta(days=7)
    prev_week = target_day - timedelta(days=7)
    
    return render_to_response('social/event.html', {'next_week': next_week, 'prev_week': prev_week, 'days': days})
        
@login_required  
def add_event(request, event_id):
    # Check if user can be here
    if not check_undergraduate(request.user.username):
        return HttpResponseForbidden()
    return HttpResponse()