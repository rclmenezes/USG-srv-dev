# help.py
# Author: Aaron Trippe
# Created July 12 2011
# Description: Renders help pages

from globalsettings import SITE_URL,SITE_EMAIL,TABLE_ENTRIES_PER_PAGE,EMAIL_HEADER_PREFIX,FBOOK_URL
from django.shortcuts import render_to_response, redirect, get_object_or_404
from rss import *
from models import *
from views import *
from forms import *

def help(request):
    login_check(request)
    return render_to_response('groups/help.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'helppage':True,
                               'alpha':request.session['alpha'],})

def help_follow(request):
    login_check(request)
    return render_to_response('groups/help_follow.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'alpha':request.session['alpha'],})


def help_account(request):
    login_check(request)
    return render_to_response('groups/help_account.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'alpha':request.session['alpha'],})


def help_officer(request):
    login_check(request)
    return render_to_response('groups/help_officer.html', 
                              {'user':request.session['user'],
                               'categories':request.session['categories'],
                               'alpha':request.session['alpha'],})

