from django.db import models
import datetime

#First name, Email, (cell phone #)
#Proxy name, Proxy email, 
#Boxes registered/paid for, Payment complete (Y/N), picked up empty box (Y/N),
#dropoff time, # boxes dropped off, 
#pickup time, # boxes reclaimed, 
    
class Status(models.Model):
    name = models.CharField(max_length=50)
    netid = models.CharField("NetID", max_length=8)
    cell_number = models.CharField("Cell Phone Number", max_length=14)
    proxy_name = models.CharField("Proxy Name", max_length=50)
    proxy_netid = models.Charfield("Proxy NetID", max_length=8)
    boxes = models.IntegerField("Number of Boxes Registered/Paid For", max_length=2)
    payment = models.BooleanField("Payment Complete")
    empty_boxes = models.BooleanField("Picked up Empty Boxes")
    dropoff_time = models.DateTimeField("Dropoff Time")
    boxes_dropped = models.IntegerField("Number of Boxes Dropped Off", max_length=2)
    pickup_time = models.DateTimeField("Pickup Time")
    boxes_picked = models.IntegerField("Number of Boxes Picked Up", max_length=2)
    
    def __unicode__(self):
        return self.name
