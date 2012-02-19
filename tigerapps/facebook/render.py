from django import shortcuts
from datetime import datetime

def render_to_response(request,template,dict):
	
	return shortcuts.render_to_response(template, dict)