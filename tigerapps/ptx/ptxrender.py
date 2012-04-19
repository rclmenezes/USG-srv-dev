from ptx.navbar import getnavbar
from ptx.models import User
from django import shortcuts
from django.http import HttpResponseRedirect


def getlogstatus(request):
    linktohelp = '<a href="/help">Help</a>'
    if request.user.is_authenticated():
        linktoprofile = '<a href="/account">My Account</a>'
        linktologout = '<a href="/logout">Log out</a>'
        return "Welcome, %s. %s | %s | %s" % (
            request.user.username,
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
    if request.user.is_authenticated():
        dbusers = User.objects.filter(net_id=request.user.username)
        if len(dbusers) == 0:
            return HttpResponseRedirect('/logout')

    dict['login_status'] = getlogstatus(request)
    dict['navbar'] = getnavbar(request)
    return shortcuts.render_to_response(template, dict)

