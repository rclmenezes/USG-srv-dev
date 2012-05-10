'''
Allows us to integrate with cal.models.Event

Should be a Manager, but we really, really don't care since we want to put
this in pom/ and not cal/.
'''
from cal.models import Event
from pom.bldg_info import *
import datetime, time
from django.db.models import Q

    
def all():
    '''
    Get all events
    '''
    return Event.objects.all().order_by('event_date_time_start','event_date_time_end')


def filter_by_bldg(qset, bldg_code):
    '''
    Get all events for `bldg_code`
    '''
    if qset:
        return qset.filter(event_location=bldg_code).order_by('event_date_time_start','event_date_time_end')
    else:
        return Event.objects.filter(event_location=bldg_code).order_by('event_date_time_start','event_date_time_end')


def filter_by_date(qset, leftMonth, leftDay, leftYear, leftHour, rightMonth, rightDay, rightYear, rightHour):
    '''
    OLD: Get all events between a range of dates
    XXX: DONT FORGET TO CHANGE THIS. YEAR SHOULD NOT HAVE THE -1 IN IT!!!!!
    '''
    left = datetime.datetime(year = int(leftYear) -1, month = int(leftMonth), day = int(leftDay), hour = int(leftHour))
    right = datetime.datetime(year = int(rightYear) -1, month = int(rightMonth), day = int(rightDay), hour = int(rightHour))
    if qset:
        return qset.filter(event_date_time_start__gte=left, event_date_time_end__lte=right).order_by('event_date_time_start','event_date_time_end')
    else:
        return Event.objects.filter(event_date_time_start__gte=left, event_date_time_end__lte=right).order_by('event_date_time_start','event_date_time_end')


def filter_by_day_hour(qset,
                   leftMonth, leftDay, leftYear, leftHour, leftMinutes,
                   rightMonth, rightDay, rightYear, rightHour, rightMinutes):
    '''
    Get all events between a range of dates and hours within those dates
    XXX: DONT FORGET TO CHANGE THIS. YEAR SHOULD NOT HAVE THE -1 IN IT!!!!!
    '''
    
    left = datetime.datetime(year = int(leftYear) -1, month = int(leftMonth), day = int(leftDay), hour = int(leftHour), minute = int(leftMinutes))
    right = datetime.datetime(year = int(rightYear) -1, month = int(rightMonth), day = int(rightDay), hour = int(rightHour), minute = int(rightMinutes))

    if qset:
        temp = qset.filter(event_date_time_start__gte=left, event_date_time_end__lte=right).order_by('event_date_time_start','event_date_time_end')
    else:
        temp = Event.objects.filter(event_date_time_start__gte=left, event_date_time_end__lte=right).order_by('event_date_time_start','event_date_time_end')
    
    retlist = []
    for x in temp:
        if (int(rightHour) > int(leftHour)):
            if x.event_date_time_start.hour >= int(leftHour) and x.event_date_time_start.hour <= int(rightHour):
                if (x.event_date_time_start.hour == int(rightHour)):
                    if (x.event_date_time_start.minute <= int(rightMinutes)):
                        retlist.append(x)
                elif x.event_date_time_start.hour == int(leftHour):
                    if (x.event_date_time_start.minute >= int(leftMinutes)):
                        retlist.append(x)
                else:
                        retlist.append(x)
        else:
            if (x.event_date_time_start.hour >= int(leftHour) or x.event_date_time_start.hour <= (int(rightHour)%24)):
                if (x.event_date_time_start.hour == int(rightHour)):
                    if (x.event_date_time_start.minute <= int(rightMinutes)):
                        retlist.append(x)
                elif x.event_date_time_start.hour == int(leftHour):
                    if (x.event_date_time_start.minute >= int(leftMinutes)):
                        retlist.append(x)
                else:
                        retlist.append(x)
    return retlist


def filter_by_title_desc(qset, query):
    '''
    Get all events with `query` in their title or description
    '''
    if qset:
        return qset.filter(Q(event_cluster__cluster_title__icontains=query) |
                           Q(event_clusert__cluster_description__icontains=query))
    else:
        return Event.objects.filter(Q(event_cluster__cluster_title__icontains=query) |
                                    Q(event_clusert__cluster_description__icontains=query))
        
        
