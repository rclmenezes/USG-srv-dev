from ptx.navbar import getnavbar
from ptx.models import User
from django import shortcuts
from django.http import HttpResponseRedirect

#temporary
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


def render_to_response(request, template, dict):
    if logged_in(request):
        user = request.session['user_data']
        dbusers = User.objects.filter(net_id=user.net_id)
        if len(dbusers) == 0:
            return HttpResponseRedirect('/logout')
        else:
            request.session['user_data'] = dbusers[0]

    dict['login_status'] = getlogstatus(request)
    dict['navbar'] = getnavbar(request)
    return shortcuts.render_to_response(template, dict)

