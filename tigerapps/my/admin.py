from models import *
from django.contrib import admin

class MyAppAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Description", {'fields': ['name', 'description', 'category', 'viewName', 'link', 'posted']}),
        ("Important Stuff", {'fields': ['myappType', 'scrolling', 'settings', 'sHeight', 'mHeight', 'preference']})
    ]
    list_display = ('myappID', 'name', 'myappType')
    search_fields = ['name']
    
class MyAppRelationAdmin(admin.ModelAdmin):
    list_display = ('relationID', 'myapp', 'column', 'sort_no', 'collapsed')
    
class PageAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'myapps', 'orderNo']})
    ]
    list_display = ('pageID', 'name', 'orderNo')
    
class AccountAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['netid', 'pages']})
    ]
    list_display = ('accountID', 'netid')
    
class CacheAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['url', 'posted']})
    ]
    list_display = ('url', 'posted')
    
admin.site.register(Page, PageAdmin)
admin.site.register(MyApp, MyAppAdmin)
admin.site.register(MyAppRelation, MyAppRelationAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(PageCache, CacheAdmin)
admin.site.register(Setting)
