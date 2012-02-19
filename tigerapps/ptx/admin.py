from ptx.models import *
from django.contrib import admin

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author')



admin.site.register(Book)
admin.site.register(Course)
admin.site.register(User)
admin.site.register(Offer)
admin.site.register(Request)

