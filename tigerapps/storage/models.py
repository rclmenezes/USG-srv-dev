from django.db import models
from django.contrib.auth.models import User
import datetime



class DropoffPickupTime(models.Model):
    '''
    User's selection from possible dropoff and pickup times of an order
    '''
    dropoff_time = models.DateTimeField("Dropoff Time", blank=True, null=True)
    pickup_time = models.DateTimeField("Pickup Time", blank=True, null=True)

    def __unicode__(self):
        return "Dropoff: %s, Pickup: %s" % (self.dropoff_time.strftime("%m/%d/%Y %I:%M%p"),
                           self.pickup_time.strftime("%m/%d/%Y %I:%M%p"))


class Status(models.Model):
    '''
    All info describing a student's order
        User: Name, Email
        Cell phone #
        Proxy name, Proxy email, 
        # Boxes registered/paid for,
        picked up empty box (Y/N),
        dropoff time, # boxes dropped off, 
        pickup time, # boxes picked up, 
    '''
    
    user = models.ForeignKey(User, related_name="status")
    dropoff_pickup_time = models.ForeignKey(DropoffPickupTime, related_name = "status")
    cell_number = models.CharField("Cell phone number", max_length=14)
    proxy_name = models.CharField("Proxy name", max_length=50, blank=True)
    proxy_email = models.CharField("Proxy email", max_length=50, blank=True)
    n_boxes_paid = models.IntegerField("Number of Boxes Paid For", max_length=2)
    bool_boxes_empty = models.BooleanField("Picked up Empty Boxes", blank=True, default=False)
    n_boxes_dropped = models.IntegerField("Number of Boxes Dropped Off", max_length=2, blank=True, default=0)
    n_boxes_picked = models.IntegerField("Number of Boxes Picked Up", max_length=2, blank=True, default=0)
    
    def __unicode__(self):
        return self.user.username
    
    class Meta:
        verbose_name_plural = 'Statuses'
