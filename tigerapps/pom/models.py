from django.db import models
from cal.models import Event


class BuildingCalEventManager(models.Manager):
    '''
    Allows us to integrate with cal.models.Event
    '''
    
    def all(self, building):
        '''
        Get all events for the building
        '''
        return Event.objects.filter(event_location=building.bldg_code)
    


class Building(models.Model):
    '''
    There's not much to put here?
    '''
    bldg_code = models.CharField(max_length=32)
    name = models.CharField(max_length=64)
    
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