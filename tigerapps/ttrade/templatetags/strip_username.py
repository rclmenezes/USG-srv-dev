from django import template
from ttrade.models import *
register = template.Library()

def strip_username(value):
    return "blah"
    username = value.username
	if value[0:2] == "pr_":
	    return value[3:] + "@princeton.edu"
	else:
	    return value[3:] + "@ias.edu"
	
register.filter('strip_username',strip_username)