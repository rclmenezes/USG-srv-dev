################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  cauth.py
# Info :  central authentication system integration
################################################################

from django.http import *
from django.contrib.auth import login
from datetime import datetime
import re, string, urllib
from django_cas.urllib2_sslv3 import urllib2
from models import *
from django.core.exceptions import ObjectDoesNotExist
from dsml import gdi
from globalsettings import *
from usermsg import MsgMgr

def login(request):
	""" Conduct login of user using a CAS system """
	if request.method == 'GET' and 'ticket' in request.GET:
		if request.session.test_cookie_worked():
			request.session.delete_test_cookie()
			try:
				ticket = request.GET.get('ticket', None)
				params = urllib.urlencode({'service':our_site_validate,'ticket':ticket})
				validation = urllib2.urlopen(cas_url+'/validate?'+params).readlines()
				if len(validation) == 2 and re.match('yes', validation[0]) != None:
					netid = validation[1].strip()
					request.session['user_data'] = login_user(netid)
					if not request.session['user_data'].user_last_login:
						request.session['user_data'].set_logged_in()
						MsgMgr.push(request, 'It looks like you\'re new here. Please confirm the information below, and then we\'ll send you along.', 1)
						#Future Feature: For new users, add tips to top of page for first-time visit
						MsgMgr.push(request, 'This page will show you updates.',2,msg_to_page='/user/messages')
						MsgMgr.push(request, 'This page will show you events you\'ve added to your calendar.',2,msg_to_page='/user/events')
						return HttpResponseRedirect('/user?newbie=True')
					request.session['user_data'].set_logged_in()
					MsgMgr.push(request, 'Welcome back, %s!' % (request.session['user_data'].casual_name()), 1)
				else:
					MsgMgr.push(request, 'You could not be logged in.', 0)	
					return HttpResponseRedirect("/")
				if 'login_redirect' in request.session:
					referrer = request.session['login_redirect']
					del request.session['login_redirect']
					return HttpResponseRedirect(referrer)
				else:
					return HttpResponseRedirect(our_site)	
			except:
				MsgMgr.push(request, 'Login failed.', 0)	
				return HttpResponseRedirect(our_site)	
		else:
			return HttpResponseRedirect('/nocookie')
	else:
		return login_redirect(request)

def login_redirect(request, path = None):
	""" Redirect to the login URL """
	if path:
		request.session['login_redirect'] = path
	params = urllib.urlencode({'service':our_site_validate})
	request.session.set_test_cookie()
	return HttpResponseRedirect(cas_url+'login?'+params)

def logout(request):
	""" Log out the user (but keep other session info) """
	try:
		del request.session['user_data']
	except:
		pass
	MsgMgr.push(request, 'You have successfully been logged out.', 1)
	lurl = cas_url + 'logout?' + urlencode({'service': our_site})
	return HttpResponseRedirect(lurl)		

def current_user(request):
	""" Get the current user, or return None """
	if 'user_data' in request.session:
		user = request.session['user_data']
		return user
	else:
		return None
	
def login_user(netid):
	""" Process a login with a certain NetID """
	user = None
	try:
		user = CalUser.objects.get(user_netid=netid)
	except ObjectDoesNotExist:
		user = make_new_user(netid)
		user.user_last_login = None
	return user
		
def make_new_user(netid):
	""" Add a new user account to the system """
	user_info = gdi(netid)
	email = user_info.get('mail', '%s@princeton.edu' % (netid))
	
	if 'pustatus' in user_info:
		if user_info['pustatus'] == 'undergraduate' and 'puclassyear' in user_info:
			pustatus = 'u'+user_info['puclassyear'][2:]
		elif user_info['pustatus'] == 'graduate' and 'puacademiclevel' in user_info:
			pustatus = 'g'+user_info['puacademiclevel']
		else:
			pustatus = user_info['pustatus'][:3]
	else:
		pustatus = 'non'				
	newbie = CalUser(
				user_netid = netid,
				user_firstname = user_info.get('givenName', ''),
				user_lastname = user_info.get('sn', ''),
				user_email = email,
				user_pustatus = pustatus,
				user_dept = user_info.get('ou', ''),
				user_last_login = datetime.now(),
				user_privacy_enabled=False, 
				user_reminders_requested=True,
				user_notify_invitation=True)
	newbie.save()
	return newbie
	
