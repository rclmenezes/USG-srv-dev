# groups.py
# Author: Aaron Trippe
# Created June 16 2011
# Description: Functions for browsing groups

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db.models import Q
from models import *
from views import *
from forms import *

def leadership(request):
    login_check(request)
    return render_to_response('groups/leadership.html',
                              {'user':request.session['user']})
