from django.db import models
from cal.models import Event
import datetime, time


"""
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