# views.py
# Author: Aaron Trippe
# Create June 15 2011
# Description: Common functions

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db.models import Q
from models import *
from dsml import gdi

alpha = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def login_check(request):
    """Checks if a user is currently logged in.

    If the user just logged in, sets up his/her session
    data.  This function should be called wherever an html
    request is sent to the server."""

    # Check login status
    try:
        if request.session['login']:
            return True
        else:
            if request.user.is_authenticated():  # User just logged in
                curr_user = request.user
            else:  # No user logged in
                return False
    except:  # Session not set up
        request.session['login'] = False
        request.session['user'] = None
        request.session['alpha'] = alpha
        request.session['categories'] = Category.objects.all().order_by('h_name')
        return False

    # Look up user in DB
    try:
        stu = Student.objects.get(netid=curr_user.username)
    except:  # User's first time; do ldap lookup and store in DB
        try:
            stu_info = gdi(curr_user.username)
            stu = Student(netid=curr_user.username, first_name=stu_info['givenName'], last_name=stu_info['sn'], email=curr_user.username+'@princeton.edu', year=int(stu_info['puclassyear']))
        except:
            stu = Student(netid=curr_user.username, email=curr_user.username+'@princeton.edu',first_name='Unknown',last_name='Unknown')
        stu.save()

    # Set up session
    request.session['login'] = True
    request.session['user'] = stu
    request.session['alpha'] = alpha
    request.session['categories'] = Category.objects.all().order_by('h_name')
    return True

def officer_check(request, group):
    """Returns True iff user associated with <request> is an officer
    in <group>.

    <group> should be a group object, not an id."""

    if not login_check(request):
        return False
    try:
        mship = Membership.objects.get(student=request.session['user'], group=group, type = 'O')
        return True
    except:
        return False

def logout(request):
    request.session.clear()
    return redirect('/accounts/logout')

def redirect_index(request):
    """Redirects non-existent pages to the index."""
    return redirect('/')

def index(request):
    """Renders primary page."""
    login_check(request)
    entries = Entry.objects.all()[:5]
    return render_to_response('groups/index.html', 
                              {'user':request.session['user'],
                               'entries':entries,
                        'categories':request.session['categories'],})
