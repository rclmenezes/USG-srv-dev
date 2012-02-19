from ptx.ptxlogin import getlogstatus, logged_in
from ptx.navbar import getnavbar
from ptx.models import User
from django import shortcuts
from django.http import HttpResponseRedirect

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

