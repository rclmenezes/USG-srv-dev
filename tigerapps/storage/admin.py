from models import *
from django.contrib import admin

class StatusAdmin(admin.ModelAdmin):
    #fieldsets = [
    #    (None, {'fields': ['user', 'title', 'entry', 'entry_description', 'description', 'time_start', 'time_end', 'poster']})
    #]
    list_display = ('user', 'cell_number', 'n_boxes_paid')
    
admin.site.register(Status, StatusAdmin)
admin.site.register(DropoffPickupTime)

'''
    user = models.ForeignKey(User, related_name="status")
    cell_number = models.CharField("Cell Phone Number", max_length=14)
    proxy_name = models.CharField("Proxy Name", max_length=50, blank=True)
    proxy_email = models.CharField("Proxy Email", max_length=50, blank=True)
    n_boxes_paid = models.IntegerField("Number of Boxes Paid For", max_length=2)
    bool_boxes_empty = models.BooleanField("Picked up Empty Boxes", blank=True, default=False)
    dropoff_time = models.DateTimeField("Dropoff Time", blank=True, null=True)
    n_boxes_dropped = models.IntegerField("Number of Boxes Dropped Off", max_length=2, blank=True, default=0)
    pickup_time = models.DateTimeField("Pickup Time", blank=True, null=True)
    n_boxes_picked = models.IntegerField("Number of Boxes Picked Up", max_length=2, blank=True, default=0)
    '''