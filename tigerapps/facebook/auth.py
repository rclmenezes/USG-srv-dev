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
#from django.contrib.auth import login
from datetime import datetime
import urllib, re, string
#from models import User
from django.core.exceptions import ObjectDoesNotExist
from dsml import gdi
from settings import *
from models import User as FUser
import logging

def login(request):
	""" Conduct login of user using a CAS system """
	if request.method == 'GET' and 'ticket' in request.GET:
		if request.session.test_cookie_worked():
			request.session.delete_test_cookie()
			ticket = request.GET.get('ticket', None)
			params = urllib.urlencode({'service':OUR_SITE_VALIDATE,'ticket':ticket})
			validation = urllib.urlopen(CAS_URL+'validate?'+params).readlines()
			if len(validation) == 2 and re.match('yes', validation[0]) != None:					
				netid = validation[1].strip()
				user =  login_user(netid)
				if not user:
					return HttpResponseRedirect('/nouserfound')
				request.session['user_netid'] = netid
				request.session['user_data'] = user
				# request.session['user_data'] = login_user(netid)
# 					if not request.session['user_data'].user_last_login:
# 						request.session['user_data'].set_logged_in()
# 						return HttpResponseRedirect('/myprofile')
# 					request.session['user_data'].set_logged_in()
				#MsgMgr.push(request, 'Welcome back, %s!' % (request.session['user_data'].casual_name()), 1)
			else:
				#MsgMgr.push(request, 'You could not be logged in.', 0)	
				return HttpResponseRedirect("/")
			if 'login_redirect' in request.session:
				referrer = request.session['login_redirect']
				del request.session['login_redirect']
				return HttpResponseRedirect(referrer)
			else:
				return HttpResponseRedirect(SITE_URL)	
			# except:
# 				#MsgMgr.push(request, 'Login failed.', 0)	
# 				return HttpResponseRedirect(SITE_URL)	
		else:
			return HttpResponseRedirect('/nocookie')
	else:
		return login_redirect('/nocookie1')

def login_redirect(request, path = None):
	""" Redirect to the login URL """
	if path:
		request.session['login_redirect'] = path
	params = urllib.urlencode({'service':OUR_SITE_VALIDATE})
	request.session.set_test_cookie()
	return HttpResponseRedirect(CAS_URL+'login?'+params)

def logout(request):
	""" Log out the user (but keep other session info) """
	try:
		del request.session['user_data']
	except:
		pass
	#MsgMgr.push(request, 'You have successfully been logged out.', 1)
	lurl = CAS_URL + 'logout'#?' + urlencode({'service': SITE_URL})
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
		user = FUser.objects.get(user_netid=netid)
	except ObjectDoesNotExist:
		user = None
		pass
		##user = make_new_user(netid)
		##user.user_last_login = None
	return user
		
# def make_new_user(netid):
# 	""" Add a new user account to the system """
# 	user_info = gdi(netid)
# 	email = user_info.get('mail', '%s@princeton.edu' % (netid))
# 	newbie = CalUser(
# 				user_netid = netid,
# 				user_firstname = user_info.get('givenName', ''),
# 				user_lastname = user_info.get('sn', ''),
# 				user_email = email,
# 				user_pustatus = user_info.get('pustatus', ''),
# 				user_dept = user_info.get('ou', ''),
# 				user_last_login = datetime.now(),
# 				user_privacy_enabled=False, 
# 				user_reminders_requested=True,
# 				user_notify_invitation=True)
# 	newbie.save()
# 	return newbie
	
