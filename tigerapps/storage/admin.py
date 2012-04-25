from models import *
from django.contrib import admin

class PostAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['title', 'content']})
    ]
    list_display = ('title',)
    search_fields = ['title', 'content']

class TimeAdmin(admin.ModelAdmin):
    list_display = ('dropoff_time', 'pickup_time', 'n_boxes_total', 'n_boxes_bought')
    
    
class OrderAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['user', 'cell_number', 'n_boxes_bought']})
    ]
    list_display = ('user', 'cell_number', 'n_boxes_bought')
    search_fields = ['user']
    

admin.site.register(Post, PostAdmin)
admin.site.register(DropoffPickupTime, TimeAdmin)
admin.site.register(UnpaidOrder, OrderAdmin)
admin.site.register(Order, OrderAdmin)
