'''
Allows us to integrate with cal.models.Event

Should be a Manager, but we really, really don't care since we want to put
this in pom/ and not cal/.
'''
from cal.models import Event
from pom.bldg_info import *
import datetime, time

    
def all():
    '''
    Get all events
    '''
    return Event.objects.all()

def bldg_filtered(bldg_code):
    '''
    Get all events for `building`
    '''
    return Event.objects.filter(event_location=bldg_code)

def date_filtered(leftMonth, leftDay, leftYear, leftHour, rightMonth, rightDay, rightYear, rightHour):
    '''DONT FORGET TO CHANGE THIS. YEAR SHOULD NOT HAVE THE -1 IN IT!!!!!'''
    #TODO: above
    left = datetime.datetime(year = int(leftYear) -1, month = int(leftMonth), day = int(leftDay), hour = int(leftHour))
    right = datetime.datetime(year = int(rightYear) -1, month = int(rightMonth), day = int(rightDay), hour = int(rightHour))
    return Event.objects.filter(event_date_time_start__gte=left, event_date_time_end__lte=right)

