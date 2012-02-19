################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  views_ajax.py
# Info :  called by AJAX on pages
################################################################

from django.http import *
from models import *
from dsml import namelookup

def netidlookup(request):
	""" Return a formatted HTML chunk of the names found using the DSML for the query """
	lookup =  namelookup(request.POST['netid'])
	html = '<div id="invite_results"><h4>Search Results</h4>'
	if lookup:
		html = html + '<ul>'
		for result in lookup:
			if 'mail' in result and 'uid' in result and 'displayName' in result:
				html = html	+ '<li><a href="#" onClick="$(\'#invitee\').val(\''+result['uid']+'\'); document.invitation.submit();">' + result['displayName'] + ' (' + result['uid']+ ')</a></li>'
			elif 'mail' in result and 'uid' in result:
				html = html	+ '<li><a href="#" onClick="$(\'#invitee\').val(\''+result['uid']+'\'); document.invitation.submit();">' + result['mail'] + ' (' + result['uid']+ ')</a></li>'
		
		html = html + '</ul>'
		html = html + '<p>Click a name to select as recipient.</p></div>'
	else:
		html = html + '<p>No results found.</p></div>'
		
	return HttpResponse(html)
	
def allguests(request):
	""" Return an HTML chunk with all names of event attendees """
	eventid = request.POST['eventid']
	try:
		event = Event.objects.get(pk = eventid)
	except:
		return
	html = '<ol>'
	attendees = RSVP.objects.filter(rsvp_event = event, rsvp_type = 'Accepted', rsvp_user__user_privacy_enabled = False).order_by('rsvp_user__user_netid')

	for rsvp in attendees:
		html = html + "<li>%s</li>" % (rsvp.rsvp_user.full_name_suffix())

	private = RSVP.objects.filter(rsvp_event = event, rsvp_type = 'Accepted', rsvp_user__user_privacy_enabled = True).count()
	if private:
		html = html + '<li class="extra">%s private guest%s</li>' % (private,('s' if private != 1 else ''))

	html = html + '</ol>'


	return HttpResponse(html)