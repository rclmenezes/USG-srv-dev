from django import template
from ttrade.models import *
from datetime import datetime
register = template.Library()

def time_difference(value):
	diff = value - datetime.now()
	if diff.days < 0:
	    diff = -diff
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