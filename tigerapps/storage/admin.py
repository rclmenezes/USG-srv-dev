from models import *
from django.contrib import admin

class PostAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['title', 'content']})
    ]
    list_display = ('title',)
    search_fields = ['title', 'content']

class TimeAdmin(admin.ModelAdmin):
    list_display = ('slot_id', 'n_boxes_total', 'n_boxes_bought',
                    'dropoff_date', 'dropoff_time_start', 'dropoff_time_end',
                    'pickup_date', 'pickup_time_start', 'pickup_time_end')
    
    
class UnpaidOrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'cell_number', 'n_boxes_bought')
    search_fields = ['user', 'proxy_name', 'proxy_email']
    
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'cell_number', 'n_boxes_bought',
                    'proxy_name', 'proxy_email', 'dropoff_pickup_time',
                    'bool_picked_empty', 'n_boxes_dropped', 'n_boxes_picked')
    search_fields = ['user', 'proxy_name', 'proxy_email']
    

admin.site.register(Post, PostAdmin)
admin.site.register(DropoffPickupTime, TimeAdmin)
admin.site.register(UnpaidOrder, UnpaidOrderAdmin)
admin.site.register(Order, OrderAdmin)
