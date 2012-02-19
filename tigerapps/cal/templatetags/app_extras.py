################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  app_extras.py
# Info :  custom template filters
################################################################

from django import template
from cal.models import EventFeature
from datetime import datetime
register = template.Library()

def dict_get(value, arg):
   return value[arg]

register.filter('dict_get',dict_get)

def time_difference(value):
	diff = datetime.now() - value
	value = 0;
	unit = "";
	if diff.days > 0:
		value = diff.days
		unit = "day"
	elif diff.seconds/(3600) > 0:
		value = diff.seconds/(3600)
		unit = "hour"
	elif diff.seconds/60 > 0:
		value = diff.seconds/60
		unit = "minute"
	else:
		value = 0
		unit = "moment"
	
	ret = str(value) + " " + unit
	if value != 1:
		ret = ret + "s"
	
	return ret
	
register.filter('time_difference',time_difference)