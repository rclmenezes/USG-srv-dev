from models import *
from adminsites import moviesAdmin
from django.contrib import admin

moviesAdmin.register(USG_Movie)
admin.site.register(USG_Movie)