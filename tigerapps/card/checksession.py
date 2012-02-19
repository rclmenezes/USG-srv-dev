# -------------------------------------------------------------------#
# checksession.py                                                    #
# Written by Betina Evancha, Sarah Wellons, Michael Gordon, and      #
# Aaron Trippe                                                       #
# Description: Functions for creating and adding meals and exchanges #
# to the database, as well as for mediating meal checking sessions.  #
# -------------------------------------------------------------------#

from datetime import datetime, date as make_date, timedelta
from django.shortcuts import render_to_response, redirect, get_object_or_404
from card.models import Member, Meal, Exchange, Club, MEAL_CHOICES

def open_session(request, netid):
    """Renders the page for opening a new checking session.

    A checking session is a period associated with a meal, a
    date, and a checker that is isolated from the checker's
    personal data and non-session functionality.  It allows
    checking and registering meals/members via both a card
    swipe or manually."""
    
    # Verify that the session is valid
    try:
        netid0 = request.session['netid']
    except:
        return redirect('/index/')
    if netid != netid0 or not request.session['login_cas']:
        return redirect('/index/')

    # Verify user is indeed a checker
    user = get_object_or_404(Member, netid=netid)
    role = user.access
    if user.access == 'M':
        return redirect('/index/')

    club = user.club
    name = user.full_name

    # If form data was submitted
    if request.method == "POST" and 'netid' in request.POST and 'meal' in request.POST:
        # verify form data
        if request.POST['netid'] != netid  or request.POST['meal'] not in MEAL_CHOICES:
            return render_to_response('card/session.html',
                                      {'netid': netid,
                                       'club': club,
                                       'role': role,
                                       'name': name})
        # Store info in request.session
        request.session['meal'] = request.POST['meal']
        request.session['datetime'] = datetime.now()
        request.session['check_session'] = True
        request.session['login_cas'] = False
        request.session['login_session'] = True
        request.session['meals'] = []
        request.session['members'] = []
        request.session.set_expiry(0)

        if 'sess_start' in request.session:
            redir = '/' + netid + '/session/' + request.session['sess_start'] + '/'
            del request.session['sess_start']
        else:
            redir = '/' + netid + '/session/add/'
            
        return redirect(redir)
            
    # Display session form
    return render_to_response('card/session.html',
                              {'netid': netid,
                               'club': club,
                               'role': role,
                               'name': name})

def open_session_reg(request, netid):
    request.session['sess_start'] = 'register'
    return open_session(request, netid)

def open_session_check(request, netid):    
    request.session['sess_start'] = 'add'
    return open_session(request, netid)

def check_session(request, netid):
    """Renders an in-session page for adding meal exchanges."""

    # Verify that the session is valid
    try:
        netid0 = request.session['netid']
    except:
        return redirect('/index/')
    if netid != netid0 or not request.session['login_session']:
        return redirect('/index/')
    user = get_object_or_404(Member, netid=netid)
    if user.access == 'M':
        return redirect('/index/')
    if 'check_session' not in request.session or not request.session['check_session']:
        return redirect('/index/')

    errmes = None
    confirm = None
    club = user.club

    if 'confirm' in request.POST:
        try:
            newmeal = makeexchange(netid, request.session['meal'], request.POST['host'], request.POST['guest'])
        except Exception, e:
            errmes = '%s'%(e,)
        else:
            confirm = 'Meal successfully exchanged'
            list = request.session['meals']
            list.append(newmeal)
            request.session['meals'] = list

        return render_to_response('card/check_session.html',
                                  {'netid':netid,
                                   'onload':'select_elem()',
                                   'confirm':confirm,
                                   'errmes': errmes,
                                   'meal': request.session['meal'],
                                   'meals': request.session['meals'],
                                   'club': club})    
    elif 'host_input' in request.POST:
        return check_swipe(request, netid)
    elif 'host' in request.POST:
        return check_man_session(request, netid)


    return render_to_response('card/check_session.html',
                              {'netid':netid,
                               'errmes': errmes,
                               'onload':'select_elem()',
                               'meal': request.session['meal'],
                               'meals': request.session['meals'],
                               'club': club})

def check_swipe(request,netid):
    """Function for checking meals via card swiping input."""

    # Get/check puids
    errmes = None
    confirm = None
    if 'host_input' not in request.POST:
        errmes = 'Error: no card swipe input from the host.'
    elif 'guest_input' not in request.POST:
        errmes = 'Error: no card swipe input from the guest.'
    else:
        s = request.POST['host_input'].split(';601621')
        t = s[1]
        host_puid = t[:9]
        s = request.POST['guest_input'].split(';601621')
        t = s[1]
        guest_puid = t[:9]
        if not host_puid.isdigit() or not guest_puid.isdigit():
            errmes = 'Error: card input in incorrect format.'

    if not errmes:
        checker = Member.objects.get(netid=netid)
        club = checker.club
        try:
            h = Member.objects.get(puid=host_puid)
            if not h.is_active:
                raise Exception
        except:
            return render_to_response('card/check_session.html',
                                      {'netid': netid,
                                       'errmes':'Error: Host is not registered with the system.',
                                       'onload':'select_elem()',
                                       'meal': request.session['meal'],
                                       'meals':request.session['meals'],
                                       'club': club})
        try:
            g = Member.objects.get(puid=guest_puid)
            if not g.is_active:
                raise Exception
        except:
            return render_to_response('card/check_session.html',
                                      {'netid': netid,
                                       'errmes':'Error: Guest is not registered with the system.',
                                       'onload':'select_elem()',
                                       'meal': request.session['meal'],
                                       'meals':request.session['meals'],
                                       'club': club})

        # Error checking
        if h == g:
            errmes = 'Error: host and guest cannot be the same.'
        elif h.club != checker.club:
            errmes = "Error: host and checker must be from the same club."

    if errmes:
        return render_to_response('check_session.html',
                                  {'netid': netid,
                                   'errmes': errmes,
                                   'onload':'select_elem()',
                                   'meal': request.session['meal'],
                                   'meals':request.session['meals'],
                                   'club': club})
    else:
        return render_to_response('check_session.html',
                                  {'netid': netid,
                                   'host': h,
                                   'guest': g,
                                   'onload':'select_elem()',
                                   'meal': request.session['meal'],
                                   'meals':request.session['meals'],
                                   'club': club})

def check_man_session(request, netid):
    
    checker = Member.objects.get(netid=netid)
    club = checker.club
    errmes = None
    host_netid = request.POST['host']
    guest_netid = request.POST['guest']

    try:
        h = Member.objects.get(netid=request.POST['host'])
        if not h.is_active:
            raise Exception
    except:
        return render_to_response('check_session.html',
                                  {'netid': netid,
                                   'errmes':'Error: Host is not registered with the system.',
                                   'onload':'select_elem()',
                                   'host_netid':host_netid,
                                   'guest_netid':guest_netid,
                                   'meal': request.session['meal'],
                                   'meals':request.session['meals'],
                                   'club': club})
    try:
        g = Member.objects.get(netid=request.POST['guest'])
        if not g.is_active:
            raise Exception
    except:
        return render_to_response('check_session.html',
                                  {'netid': netid,
                                   'errmes':'Error: Guest is not registered with the system',
                                   'onload':'select_elem()',
                                   'host_netid':host_netid,
                                   'guest_netid':guest_netid,
                                   'meal': request.session['meal'],
                                   'meals': request.session['meals'],
                                   'club': club})

    # Error checking
    if h == g:
        errmes = 'Error: host and guest cannot be the same.'
    elif h.club != checker.club:
        errmes = "Error: host and checker must be from the same club."

    if errmes:
        return render_to_response('check_session.html',
                                  {'netid': netid,
                                   'errmes': errmes,
                                   'host_netid':host_netid,
                                   'guest_netid':guest_netid,
                                   'onload':'select_elem()',
                                   'meal': request.session['meal'],
                                   'meals':request.session['meals'],
                                   'club': club})
    else:
        return render_to_response('check_session.html',
                                  {'netid': netid,
                                   'host': h,
                                   'guest': g,
                                   'errmes':errmes,
                                   'host_netid':host_netid,
                                   'guest_netid':guest_netid,
                                   'onload':'select_elem()',
                                   'meal': request.session['meal'],
                                   'meals':request.session['meals'],
                                   'club': club})

def remove_meal(request, netid, meal_idx):
    """Remove a meal that was added in this session."""
    
    # Verify that the session is valid
    try:
        netid0 = request.session['netid']
    except:
        return redirect('/index/')
    if netid != netid0 or not request.session['login_session']:
        return redirect('/index/')
    user = get_object_or_404(Member, netid=netid)
    if user.access == 'M':
        return redirect('/index/')
    if 'check_session' not in request.session or not request.session['check_session']:
        return redirect('/index/')

    # Check that index is in bounds
    meal_idx = int(meal_idx)
    try:
        meals = request.session['meals']
        meal = meals[meal_idx]
    except:
        return redirect('/index/')

    # Lookup and remove meal
    meal.delete()
    meals.remove(meal)
    request.session['meals'] = meals
    return redirect('/'+netid+'/session/add/')

# takes a checker netid, a meal name, a host and guest netid
def makeexchange(checker, meal, host, guest):
    """Create a meal and associate it with an Exchange object.

    Returns a confirmation/error message (a string) and the
    the new meal if it was successfully created."""
    
    # check that both host and guest are registered
    hostuser = Member.objects.filter(netid__exact=host)
    if (hostuser == []):
        raise Exception('Error: host is not registered with the system.')
    guestuser = Member.objects.filter(netid__exact=guest)
    if (guestuser == []):
        raise Exception('Error: guest is not registered with the system.')
    if (len(hostuser) != 1 or len(guestuser) != 1):
        raise Exception('Error: multiple users per netid!') # can't happen

    # TODO: no 404s at this level, better err handling
    hostuser = get_object_or_404(Member, netid=host)
    guestuser = get_object_or_404(Member, netid=guest)
    
    #check that mealchecker's club= host's club
    checkuser = get_object_or_404(Member, netid=checker)
    #return checkuser.netid
    if (checkuser.club != hostuser.club):
        raise Exception('Error: Host and meal checker must be from the same club.')
    
    #check that host's club and guest's club are different
    if (hostuser.club == guestuser.club):
        raise Exception('Error: host and guest must be from different clubs.')

    #check duplicates
    recent = Meal.objects.filter(date=make_date.today(),
                                 host=hostuser,
                                 guest=guestuser,
                                 meal_type=meal)
    if len(recent) > 0:
        raise Exception('Error: host and guest have already exchanged meals.')
                                 

    #make new meal
    newmeal = Meal(host=hostuser, guest=guestuser, checker=checkuser, meal_type=meal)
    newmeal.save()  # let exceptions propagate up
    matchex = findmatch(newmeal)
    if (matchex):
        matchex.meal_2 = newmeal
        matchex.save()
        date = matchex.meal_1.date
        confirm = 'Exchange matched with meal on ' + str(date.month)+'/'+str(date.day)+'/'+str(date.year)+'.'
    else:
        exchange=Exchange(meal_1=newmeal)
        exchange.save()
        confirm = "New exchange started!"
    return newmeal

def findmatch(meal):
    """Finds and returns a matching exchange for meal, or None
    if none exists."""
    
    # assume meal is a meal type
    # find all potential matches
    match = None
    matches = Exchange.objects.filter(meal_2__isnull=True, meal_1__host=meal.guest, meal_1__guest=meal.host, meal_1__meal_type=meal.meal_type).order_by('meal_1__date')
    if matches:
        match = matches[0]
    return match
