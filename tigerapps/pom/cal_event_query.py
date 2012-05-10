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
    Get all events for `building`
    '''
    if qset:
        return qset.filter(event_location=bldg_code).order_by('event_date_time_start','event_date_time_end')
    else:
        return Event.objects.filter(event_location=bldg_code).order_by('event_date_time_start','event_date_time_end')


def filter_by_date(qset, leftMonth, leftDay, leftYear, leftHour, rightMonth, rightDay, rightYear, rightHour):
    '''DONT FORGET TO CHANGE THIS. YEAR SHOULD NOT HAVE THE -1 IN IT!!!!!'''
    left = datetime.datetime(year = int(leftYear) -1, month = int(leftMonth), day = int(leftDay), hour = int(leftHour))
    right = datetime.datetime(year = int(rightYear) -1, month = int(rightMonth), day = int(rightDay), hour = int(rightHour))
    if qset:
        return qset.filter(event_date_time_start__gte=left, event_date_time_end__lte=right).order_by('event_date_time_start','event_date_time_end')
    else:
        return Event.objects.filter(event_date_time_start__gte=left, event_date_time_end__lte=right).order_by('event_date_time_start','event_date_time_end')


def filter_by_hour(qset, leftMonth, leftDay, leftYear, leftHour, rightMonth, rightDay, rightYear, rightHour):
    left = datetime.datetime(year = int(leftYear) -1, month = int(leftMonth), day = int(leftDay), hour = int(leftHour))
    right = datetime.datetime(year = int(rightYear) -1, month = int(rightMonth), day = int(rightDay), hour = int(rightHour))
    
    temp = res.filter(event_date_time_start__gte=left, event_date_time_end__lte=right).order_by('event_date_time_start','event_date_time_end')
    
    retlist = []
    for x in temp:
        if (rightHour > leftHour):
            if x.event_date_time_start.hour >= leftHour and x.event_date_time_start.hour <= rightHour:
                if (x.event_date_time_start.hour == rightHour):
                    if (x.event_date_time_start.minute == 0):
                        retlist.append(x)
                else:
                        retlist.append(x)
        else:
            if x.event_date_time_start.hour >= leftHour or x.event_date_time_start.hour <= (rightHour%24):
                if (x.event_date_time_start.hour == rightHour):
                    if (x.event_date_time_start.minute == 0):
                        retlist.append(x)
                else:
                        retlist.append(x)
    return retlist


def bldg_title_descr_filtered(bldg_code, query):
    return Event.objects.filter(Q(event_location=bldg_code),
                                Q(event_cluster__cluster_title__icontains=query) |
                                Q(event_clusert__cluster_description__icontains=query))
    
def title_descr_filtered(query):
    return Event.objects.filter(Q(event_cluster__cluster_title__icontains=query) |
                                Q(event_clusert__cluster_description__icontains=query))
    
