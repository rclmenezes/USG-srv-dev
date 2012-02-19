from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from ttrade import casBackend, iasBackend

def login_view(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
                return HttpResponseRedirect('http://dev.ttrade.tigerapps.org/%s' % request.GET.get('next','/'))
            else:
                # Return a 'disabled account' error message
                pass
        else:
            # Return an 'invalid login' error message.
            pass


    return render_to_response('ttrade/login.html')

def cas_login(request):
    ticket = request.GET.get('ticket', None)
    if ticket is None:
        return HttpResponseRedirect('%s?service=%s' %
                                            (casBackend.cas_login_url,
                                             casBackend.cas_ttrade_service_url))
    else:
        #validate
        user = authenticate(ticket=ticket)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
                return HttpResponseRedirect('/')
            else:
                #return inactive page
                pass
        else:
            #return user does not exist
            pass
    return HttpResponseRedirect(casBackend.cas_ttrade_service_url)
    
def cas_logout(request):
    logout(request)
    return HttpResponseRedirect(casBackend.cas_logout_url)
    
def ias_login(request):
    ticket = request.GET.get('ticket', None)
    if ticket is None:
        return HttpResponseRedirect('%s?service=%s' %
                                            (iasBackend.cas_login_url,
                                             iasBackend.cas_ttrade_service_url))
    else:
        #validate
        user = authenticate(ticket=ticket)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
                return HttpResponseRedirect('/')
            else:
                #return inactive page
                pass
        else:
            #return user does not exist
            pass
    return HttpResponseRedirect(iasBackend.cas_ttrade_service_url)

def ias_logout(request):
    logout(request)
    return HttpResponseRedirect(iasBackend.cas_logout_url)

def logout_view(request):
    if request.user.username.startswith('pr_'):
        return cas_logout(request)
    elif request.user.username.startswith('ia_'):
        return ias_logout(request)
    else:
        logout(request)
        return HttpResponseRedirect("/")
    
def login_choices(request):
    # Check if already logged in
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')

    return render_to_response('ttrade/login_choices.html')
