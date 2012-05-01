from django.db import models
from cal.models import Event
import datetime, time

class BuildingCalEventManager(models.Manager):
    '''
    Allows us to integrate with cal.models.Event
    '''
    
    def all(self):
        '''
        Get all events
        '''
        return Event.objects.all()
        
    
    def bldg_filtered(self, building):
        '''
        Get all events for `building`
        '''
        return Event.objects.filter(event_location=building.bldg_code)
    
    
    def date_filtered(self, leftMonth, leftDay, leftYear, leftHour, rightMonth, rightDay, rightYear, rightHour):
        '''DONT FORGET TO CHANGE THIS. YEAR SHOULD NOT HAVE THE -1 IN IT!!!!!'''
        #TODO: above
        left = datetime.datetime(year = int(leftYear) - 1, month = int(leftMonth), day = int(leftDay), hour = int(leftHour))
        right = datetime.datetime(year = int(rightYear) - 1, month = int(rightMonth), day = int(rightDay), hour = int(rightHour))
        return Event.objects.filter(event_date_time_start__gte=left, event_date_time_end__lte=right)


class Building(models.Model):
    '''
    There's not much to put here?
    '''
    bldg_code = models.CharField(max_length=32)
    name = models.CharField(max_length=64)
    
    has_hours = models.BooleanField(default=False)
    has_laundry = models.BooleanField(default=False)
    has_menu = models.BooleanField(default=False)
    
    objects = models.Manager()
    cal_events = BuildingCalEventManager()
    



#may not need this
"""
class BuildingCoordinates(models.Model):
    '''
    Represents zoom-specific information for each building.
    There is one of these for each building, for each zoom.
    '''
    building = models.ForeignKey(Building)
    zoom = models.IntegerField(max_length=1)
    left = models.IntegerField()
    top = models.IntegerField()
    height = models.IntegerField()
    width = models.IntegerField()
    

    class Meta:
        verbose_name_plural = "Building Coordinates"
"""