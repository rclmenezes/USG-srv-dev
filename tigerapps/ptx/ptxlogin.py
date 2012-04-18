import logging
log = logging.getLogger(__name__)

import urllib
from django_cas.urllib2_sslv3 import urllib2

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.http import QueryDict
from ptx.ptxrender import render_to_response

from ptx.models import Book, Offer, User, Course
from ptx.navbar import getnavbar

def urlopen(url):
    log.debug("Requesting %s" % url)
    return urllib2.urlopen(url)

def redirect(url):
    log.debug("Redirecting to %s" % url)
    return HttpResponseRedirect(url)

def validate(ticket, service, redirect=None):
    """Authenticates the ticket via CAS."""
    CAS = settings.CAS
    if redirect:
        service += '?redirect=' + urllib.quote(redirect)

    params = urllib.urlencode({
            'ticket': ticket,
            'service': service,
            })
    query = urlopen(CAS + 'validate?' + params)
    # Charset found by manual inspection of HTTP HEAD response.
    query = query.read().decode('iso-8859-1')
    return query

def login(url, act="login"):
    """Returns a redirect response for logging into or out of CAS."""
    CAS = settings.CAS
    url = urllib.quote(url)
    return redirect(CAS + act + '?service=' + url)

def logged_in(request):
    '''Returns True if the user is logged in'''
    return "user_data" in request.session

def getlogstatus(request):
    linktohelp = '<a href="/help">Help</a>'
    if logged_in(request):
        user_data = request.session["user_data"]
        linktoprofile = '<a href="/account">My Account</a>'
        linktologout = '<a href="/logout">Log out</a>'
        return "Welcome, %s. %s | %s | %s" % (
            user_data.net_id,
            linktoprofile,
            linktologout,
            linktohelp)
    else:
        fullurl = request.build_absolute_uri()
        if 'logout' in fullurl:
            return '<a href="/login?redirect=%s">Login</a> | %s' % (fullurl, linktohelp)
        else:
            return '<a href="/login">Login</a> | ' + linktohelp

def ptxlogout(request):
    if logged_in(request):
        # Delete the entire session.
        request.session.flush()
        url = request.build_absolute_uri()
        return login(url, act="logout")

    # if they have been logged out and redirected back, show them logout page
    return render_to_response(request, "ptx/logout.html", {})

def ptxlogin(request):
    if not request.method == "GET":
        return

    fullurl = request.build_absolute_uri()
    log.info(fullurl)
    q = request.GET

    # is this person coming back with a ticket?
    if not "ticket" in q:
        # if they are already logged in, don't bother sending them to CAS
        if logged_in(request):
            return redirect(q.get("redirect", "/"))
        else:
            return login(fullurl)

    # If so, authenticate their ticket. Strip out all GET params
    # first, except redirect.
    url = fullurl.split('?')[0]
    tquery = validate(q["ticket"], url, q.get("redirect"))

    tokens = tquery.split()
    if tokens[0] == u"yes":
        netid = tokens[1]

        # they have been authenticated, is this their first time?
        if User.objects.filter(net_id=netid).count() == 0:
            # add them as a new user
            newuser = User(net_id=netid)
            newuser.save()
            request.session['user_data'] = newuser
            return redirect('/profile?n=true')

        # they already exist
        user_data = User.objects.get(net_id=netid)
        request.session['user_data'] = user_data

    # see if this person should be redirected to where they
    # were prior to logging in
    if "redirect" in q:
        # We do not want to redirect back to a logout page.
        if not "/logout" in q["redirect"]:
            return redirect(q["redirect"])

    # otherwise redirect them to the home page
    return redirect('/')
