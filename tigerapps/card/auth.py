# -------------------------------------------------------------------#
# auth.py                                                            #
# Written by Betina Evancha, Sarah Wellons, Michael Gordon, and      #
# Aaron Trippe                                                       #
# Description: Functions for authorizing users through both CAS and  #
# django's User model and sessions.                                  #
# -------------------------------------------------------------------#

from django.shortcuts import render_to_response, redirect, get_object_or_404
from card.models import Member, Meal, Exchange, Club
from card.forms import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import *
from os import environ
from urllib import urlencode, urlopen
import re

HOSTNAME = 'http://dev.card.tigerapps.org:'

cas_url_login = 'https://fed.princeton.edu/cas/login'
cas_url_valid = 'https://fed.princeton.edu/cas/serviceValidate'
cas_url_logout = 'https://fed.princeton.edu/cas/logout'

# Functions for returning redirection urls
# NOTE: localhost vs. network urls are hard coded (due to CAS)
# and must be changed maually
def service_url(request):
    return HOSTNAME + str(request.META['SERVER_PORT']) +'/cas/'
    #return request.META['HTTP_HOST'] + '/cas/'    
def index_url(request):
    return HOSTNAME + str(request.META['SERVER_PORT']) +'/'
    #return request.META['HTTP_HOST'] + '/'
def logout_url(request):
    return HOSTNAME + str(request.META['SERVER_PORT'])# +'/logout/'
    #return request.META['HTTP_HOST'] + '/logout'
def get_redirect_url(request, next):
    return HOSTNAME + str(request.META['SERVER_PORT']) + next
    #return request.META['HTTP_HOST'] + next

def cas_redirect(request):
    """Return a redirect to the CAS login page."""
    
    url = cas_url_login + '?' + urlencode({'service':service_url(request)})
    return HttpResponseRedirect(url)

def cas_validate(request, ticket):
    """Validate a ticket through CAS.

    Return netid if valid, else return None."""
    
    url = cas_url_valid + '?' + urlencode({'service':service_url(request), 'ticket':ticket})
    valid = urlopen(url).readlines()
    if valid[1].count('<cas:authenticationSuccess>') > 0:
        s = valid[2].partition('<cas:user>')
        t = s[2].partition('</cas:user>')
        return t[0]
    return None

def cas_login(request):
    """Logs a user in using CAS.

    If already logged in, this function redirects to the member/
    checker page.  Else, it redirects to the CAS login page and
    validates the returned ticket before redirecting to the app."""

    # Log out of club account
    #if 'login' in request.session and request.session['login'] == 'club':
    #    return my_logout(request, '/cas/')

     # If in session, redirect there
    if 'login_session' in request.session and request.session['login_session']:
        return redirect('/' + request.session['netid'] + '/session/add/')

    # User just logged in; validate
    elif request.method == 'GET' and 'ticket' in request.GET:
        try:
            ticket = request.GET['ticket']
            netid = cas_validate(request, ticket)
            if not netid:
                # invalid: redirect to login page
                return redirect('/') #render_to_response('index.html')
                
            # Check that user is in the database
            try:
                m = Member.objects.get(netid=netid)
                if not m.is_active:
                    raise Exception
            except:
                request.session['login'] = 'err'
                return cas_logout(request, '/index/err')
#                return render_to_response('index.html',
#                                          {'errmes':'Error: Username not in database. Please contact your club to sign up.'})

            # Set up session data
            request.session['netid'] = netid
            request.session['login_cas'] = True
            request.session.set_expiry(0)
            
            return redirect('/' + netid + '/personal/')
        
        #return response
        except Exception, e:
            return render_to_response('card/index.html',
                                      {'errmes':'Exception: %s'%(e,)})        
    else:
        # Redirect to CAS login
        return cas_redirect(request)

def login_err(request):
    return render_to_response('card/index.html',
                              {'errmes':'Error: Username not in database. Please contact your club to sign up.'})

def club_login(request):
    """Logs a user into a club account.

    Gets user login info via a form, then checks against
    the accounts stored in the database.  If the user is
    logged in through CAS, they will be logged out
    automatically."""
    
    if 'club' in request.session:  # already logged in
        request.session['login_club'] = True
        request.session['club'] = request.user.username
        return redirect('/%s/club/' % (request.user.username))
    
    elif 'club' in request.POST and 'clubPassword' in request.POST: # log in user
        username = request.POST['club']
        password = request.POST['clubPassword']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            request.session['login_club'] = True
            request.session['club'] = user.username
            request.session.set_expiry(0)            
            return redirect('/%s/club/' % (user.username))
        return render_to_response('card/club_login.html',
                                  {'errmes':'Error: incorrect username/password combo'})

    return render_to_response('card/club_login.html')

def change_password(request, club):
    # Verify that the session is valid
    try:
        club0 = request.session['club']
    except:
        return redirect('/index/')
    if club0 != club:
        return redirect('/index/')
    #Get club
    Cclub = get_object_or_404(Club, account__username=club0)

    errmes = None
    confirm = None
    if request.method == "POST":
        if 'email' in request.POST:
            e_form = ChangeEmailForm(request.POST, instance=Cclub.account)
            form = ChangePasswordForm()
            if e_form.is_valid():
                e_form.save()
                confirm = 'Email changed'
            else:
                errmes = 'There were errors in this form'
        elif 'current_password' in request.POST:
            form = ChangePasswordForm(request.POST)
            e_form = ChangeEmailForm(instance=Cclub.account)
            if form.is_valid():
                if not Cclub.account.check_password(form.cleaned_data['current_password']):
                    form._errors["current_password"] = form.error_class(['Incorrect password'])
                else:
                    try:
                        Cclub.account.set_password(form.cleaned_data['new_password'])
                        Cclub.account.save()
                        confirm = 'Password successfully changed.'
                    except Exception, e:
                        errmes = e
            else:
                errmes = 'There were errors in the form'
    else:
        form = ChangePasswordForm()
        e_form = ChangeEmailForm(instance=Cclub.account)

    return render_to_response('card/club_password.html',
                              {'errmes': errmes,
                               'confirm': confirm,
                               'form':form,
                               'e_form':e_form,
                               'club': club})

def cas_logout(request, next=None, errmes=None):
    """Log out of CAS."""

    if 'netid' in request.session:
        del request.session['netid']
    request.session['login_cas'] = False
    request.session['login_session'] = False

    if not next:
        url = cas_url_logout + '?' + urlencode({'service':logout_url(request)})
    else:
        url = cas_url_logout + '?' + urlencode({'service':get_redirect_url(request, next)})
    return HttpResponseRedirect(url)

def club_logout(request, next=None, errmes=None):
    """Club logout function."""

    if 'club' in request.session:
        del request.session['club']
    request.session['login_club'] = False
#    logout(request)

    if next:
        return redirect(next)
    return render_to_response('card/index.html',
                              {'errmes':errmes})

