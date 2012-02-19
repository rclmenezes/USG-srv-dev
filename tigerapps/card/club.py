# -------------------------------------------------------------------#
# club.py                                                            #
# Written by Betina Evancha, Sarah Wellons, Michael Gordon, and      #
# Aaron Trippe                                                       #
# Description: Collection of functions related to club account       #
# functionality, including adding/modding meals and changing passwd  #
# -------------------------------------------------------------------#

from card.forms import *
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db.models import Q
from card.models import *
from datetime import date as make_date
from datetime import timedelta, datetime
from checksession import findmatch, check_swipe, check_man_session

def stats(request, club, graphtype):
    """Renders month-long stats for a club."""

    # Verify that the session is valid
    try:
        club0 = request.session['club']
    except:
        return redirect('/index/')
    if club0 != club:
        return redirect('/index/')

    # overall
    hostExchanges = Exchange.objects.filter(Q(meal_1__host__club__account__username=club)|Q(meal_2__host__club__account__username=club))
    hostnum = len(hostExchanges)
    guestExchanges = Exchange.objects.filter(Q(meal_1__guest__club__account__username=club)|Q(meal_2__guest__club__account__username=club))
    guestnum = len(guestExchanges)

    mealtypes = ['Breakfast', 'Brunch', 'Lunch', 'Dinner', 'Other']
    meals = []
    
    # by meal
    for meal in mealtypes:
        type = meal
        mealsout = len(Exchange.objects.filter(Q(meal_1__guest__club__account__username=club) | Q(meal_2__guest__club__account__username=club)).filter(meal_1__meal_type=type))
        mealsin = len(Exchange.objects.filter(Q(meal_1__host__club__account__username=club) | Q(meal_2__host__club__account__username=club)).filter(meal_1__meal_type=type))
        meals.append({'type': type, 'mealsout': mealsout, 'mealsin': mealsin})

    # by club
    clubmeals = []
    clubs = Club.objects.all()
    for clubex in clubs:
        clubname = clubex.name
        if (clubname.lower() != club):
            clubname = clubname.replace(' ','')
            mealsout = len(Exchange.objects.filter(Q(meal_1__guest__club__account__username=club) | Q(meal_2__guest__club__account__username=club)).filter(Q(meal_1__host__club__account__username=clubname)|Q(meal_2__host__club__account__username=clubname)))
            mealsin = len(Exchange.objects.filter(Q(meal_1__host__club__account__username=club) | Q(meal_2__host__club__account__username=club)).filter( Q(meal_1__guest__club__account__username=clubname) | Q(meal_2__guest__club__account__username=clubname)))
            clubmeals.append({'clubname': clubname, 'mealsout': mealsout, 'mealsin': mealsin})

    #meals by date
    datemeals = []
    today = date.today()
    daycount = make_date(day = 1, month = today.month, year=today.year)
    day = timedelta(days = 1)

    while (daycount.month == today.month):
        mealsout = len(Meal.objects.filter(guest__club__account__username=club).filter(date=daycount))
        mealsin = len(Meal.objects.filter(host__club__account__username=club).filter(date=daycount))
        datemeals.append({'day': daycount.day, 'mealsout': mealsout, 'mealsin': mealsin})
        daycount = daycount + day

    #did user select a graph or table?
    if (graphtype == 'graph'):
        graph = 1
    else:
        graph = None
    
    response = render_to_response('card/stats.html',
                                  {'club': club,
                                   'hostnum': hostnum,
                                   'guestnum': guestnum,
                                   'meals': meals,
                                   'clubmeals': clubmeals,
                                   'datemeals': datemeals,
                                   'graph': graph})
    return response


def club(request, club):
    """Renders the default page for club accounts."""
    
    # Verify that the session is valid
    try:
        club0 = request.session['club']
    except:
        return redirect('/index/')
    if club0 != club:
        return redirect('/index/')

    form = AddMemberForm()

    # default page is members add
    response = render_to_response('card/members_add.html',
                                  {'club': club,
                                   'form':form})
    return response

def listMembers(request, club):
    """Renders page for viewing and searching club members.
    
    Filters results based on form fields."""

    # Verify that the session is valid
    try:
        club0 = request.session['club']
    except:
        return redirect('/index/')
    if club0 != club:
        return redirect('/index/')
    
    #Get club
    Cclub = get_object_or_404(Club, account__username=club0)
    mes = ''
    
    if ('Submit' in request.GET):
        fName = request.GET['fName']
        lName = request.GET['lName']
        netID = request.GET['netID']
        Cyear = request.GET['year']
        stat  = request.GET['status']
        role  = request.GET['role']
    else:
        fName = ''
        lName = ''
        netID = ''
        Cyear = ''
        stat  = 'Active'
        role  = 'All'

    if 'bRemove' in request.POST:
        bNetIDs = request.POST.getlist('check')
        members = Member.objects.filter(netid__in=bNetIDs)
        for m in members:
            m.delete()
        mes = 'Removed members'
            
    if 'bStatus' in request.POST:
        bNetIDs = request.POST.getlist('check')
        members = Member.objects.filter(netid__in=bNetIDs)
        for m in members:
            if m.is_active:
                m.is_active = False
            else:
                m.is_active = True
            m.save()
        mes = 'Updated status.'

    if 'bRole' in request.POST:
        bNetIDs = request.POST.getlist('check')
        members = Member.objects.filter(netid__in=bNetIDs)
        for m in members:
            if m.access == 'M':
                m.access = 'C'
            else:
                m.access = 'M'
            m.save()
        mes = 'Changed membership role'
        
    # Get all matching members except the special club checker account
    ex = str(Cclub.account.username)+'check'

    if stat == 'Active':
        if role == 'All':
            members = Member.objects.filter(netid__istartswith=netID, first_name__istartswith=fName, last_name__istartswith=lName,year__icontains=Cyear).filter(club=Cclub).exclude(netid=ex).exclude(is_active=False)
        else:
            # Get Checkers
            members = Member.objects.filter(netid__istartswith=netID, first_name__istartswith=fName, last_name__istartswith=lName,year__icontains=Cyear).filter(club=Cclub).exclude(netid=ex).exclude(is_active=False).exclude(access='M')
        
    elif stat == 'Inactive':
        if role == 'All':
            members = Member.objects.filter(netid__istartswith=netID, first_name__istartswith=fName, last_name__istartswith=lName,year__icontains=Cyear).filter(club=Cclub).exclude(netid=ex).exclude(is_active=True)
        else:
            # Get Checkers
            members = Member.objects.filter(netid__istartswith=netID, first_name__istartswith=fName, last_name__istartswith=lName,year__icontains=Cyear).filter(club=Cclub).exclude(netid=ex).exclude(is_active=True).exclude(access='M')
        
    else:
        if role == 'All':
            members = Member.objects.filter(netid__istartswith=netID, first_name__istartswith=fName, last_name__istartswith=lName,year__icontains=Cyear).filter(club=Cclub).exclude(netid=ex)
        else:
            # Get Checkers
            members = Member.objects.filter(netid__istartswith=netID, first_name__istartswith=fName, last_name__istartswith=lName,year__icontains=Cyear).filter(club=Cclub).exclude(netid=ex).exclude(access='M')
        
    
    response = render_to_response('card/members_list.html',
                                  {'club': club0,
                                   'members': members,
                                   'fName': fName,
                                   'lName': lName,
                                   'netID': netID,
                                   'stat': stat,
                                   'role': role,
                                   'mes': mes,
                                   'year': Cyear })
        
    return response

def modMember(request, club, netid):
    """Renders page for modifying club members' statuses.

    Takes input from a form and modifies or removes the
    member appropriately. After modification, renders
    the modification page with the changes; after removal,
    renders the members list page passing removed==True."""
    
    # Verify that the session is valid
    try:
        club0 = request.session['club']
    except:
        return redirect('/index/')
    if club0 != club:
        return redirect('/index/')
    if netid == club+'check': # Special club checking account
        return redirect('/index/')

    Cclub = get_object_or_404(Club, account__username=club0)
    m = get_object_or_404(Member, netid=netid, club=Cclub)

    errmes = ''
    confirm = ''
    form = None
    if request.method == 'POST':
        if 'Remove' in request.POST:
            # TODO: popup box to confirm (in template)
            pnetID = netid
            m = Member.objects.get(netid=pnetID)
            m.delete()
            return redirect('/%s/members/list/'%club)
            # TODO: save filter data
            #fName = ''
            #lName = ''
            #netID = ''
            #Cyear = ''
            # Return to members list page
            #ex = str(Cclub.account.username)+'check'        
            #members = list(Member.objects.filter(netid__icontains=netID, first_name__icontains=fName, last_name__icontains=lName,year__icontains=Cyear).filter(club=Cclub).exclude(netid=ex))
            #return render_to_response('members_list.html',
            #                          {'club': club0,
            #                           'members': members,
            #                           'fName': fName,
            #                           'lName': lName,
            #                           'netID': netID,
            #                           'pnetID': pnetID,
            #                           'removed':True})
        else:
            form = ModMemberForm(request.POST, instance=m)
            if form.is_valid():
                try:
                    form.save()
                    confirm = "Member successfully modified"
                except Exception, e:
                    errmes = e
            else:
                errmes = "There were errors in the form"       
    else:
        form = ModMemberForm(instance = m)

    return render_to_response('card/members_mod.html',
                              {'club': club0,
                               'form':form,
                               'member': m,
                               'mes':confirm,
                               'errmes': errmes})
    
def addMeals(request, club):
    """Renders the page for adding meals from the club account."""
    
    # Verify that the session is valid
    try:
        club0 = request.session['club']
    except:
        return redirect('/index/')
    if club0 != club:
        return redirect('/index/')
  
    Cclub = get_object_or_404(Club, account__username=club0)

    added = False
    err = False
    errmes=''
    confirm = None

    if 'confirm' in request.POST:
        try:
            dates = request.POST['date_input'].split('/')
            date = make_date(int(dates[2]), int(dates[0]), int(dates[1]))
            host = Member.objects.get(netid=request.POST['host'])
            guest = Member.objects.get(netid=request.POST['guest'])
            confirm = makeexchange(Cclub.check, request.POST['meal_input'], host, guest, date)
        except Exception, e:
            errmes = 'Errors in form. Please reswipe.'

        return render_to_response('card/meals_add.html',
                                  {'onload':'select_elem()',
                                   'form':AddMealForm(),
                                   'confirm':confirm,
                                   'today':datetime.today().strftime('%m/%d/%Y'),
                                   'errmes': errmes,
                                   'club': club})
    elif 'host_input' in request.POST:
        return check_swipe_club(request, Cclub.check.netid)
    elif 'reset' in request.POST:
        return render_to_response('card/meals_add.html',
                                  {'onload':'select_elem()',
                                   'form':AddMealForm(),
                                   'today':datetime.today().strftime('%m/%d/%Y'),
                                   'confirm':confirm,
                                   'errmes': errmes,
                                   'club': club})

    elif request.method == 'POST':
        m = Meal(checker=Cclub.check)
        form = AddMealForm(request.POST,instance=m)
        if form.is_valid():
            try:
                h = Member.objects.get(netid=form.cleaned_data['host'])
                g = Member.objects.get(netid=form.cleaned_data['guest'])
                date = form.cleaned_data['date']
                meal = form.cleaned_data['meal_type']
                confirm = makeexchange(Cclub.check, meal, h, g, date=date)
                form = AddMealForm()
            except Exception,e:
                errmes = e
        else:
            errmes = 'There were errors in this form'
    else:
        form = AddMealForm()

    return render_to_response('card/meals_add.html',
                              {'club': club,
                               'onload':'select_elem()',
                               'today':datetime.today().strftime('%m/%d/%Y'),
                               'form':form,
                               'errmes':errmes,
                               'confirm': confirm})
    
# takes checker, host, and guest OBJ
def makeexchange(check, meal, hostuser, guestuser, date, flag=True):
    """Create a meal and associate it with an Exchange object.

    Returns a confirmation/error message (a string)."""

    checkuser = get_object_or_404(Member, netid=check)
    #check that mealchecker's club= host's club
    if (checkuser.club != hostuser.club):
        return "Error: Host must be a member of checker's club."
    
    #check that host's club and guest's club are different
    if (hostuser.club == guestuser.club):
        return 'Error: host and guest must be from different clubs.'

    #check that meal hasn't already been exchange
    #flag is hack for modifying meals
    if (flag):
        old = Meal.objects.filter(host=hostuser, guest=guestuser,date=date,
                              meal_type=meal)
        if len(old) > 0:
            return 'Error: host and guest have already exchanged during this meal.'
    
    #make new meal
    newmeal = Meal(host=hostuser, guest=guestuser, checker=checkuser, meal_type=meal, date=date)
    
    # TODO: try/except for saves
    newmeal.save()
    matchex = findmatch(newmeal)
    if (matchex):
        matchex.meal_2 = newmeal
        matchex.save()
        date = matchex.meal_1.date
        confirm = 'Exchange matched with meal on ' + date.ctime()+'.'
    else:
        exchange=Exchange(meal_1=newmeal)
        exchange.save()
        confirm = "New exchange started between "+hostuser.netid+" and "+guestuser.netid+'.'
    return confirm

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

def listMeals(request, club):
    # Verify that the session is valid
    try:
        club0 = request.session['club']
    except:
        return redirect('/index/')
    if club0 != club:
        return redirect('/index/')
    
    #Get club
    Cclub = get_object_or_404(Club, account__username=club0)
    errmsg = ''
    
    if request.method == 'GET':
        try:
            memberID = request.GET['memberID']
            otherID = request.GET['otherID']
            oClub = request.GET['oClub']
            status = request.GET['status']
            date = request.GET['date']
            meal = request.GET['meal']
            iChecker = request.GET['oChecker']
        except:
            memberID = ''
            otherID = ''
            oClub = ''
            status = ''
            date = ''
            meal = ''
            date_obj = None
            iChecker = ''


        if (iChecker.lower() == 'club'):
            oChecker = 'check'
        else:
            oChecker = iChecker

        if meal == 'Any':
            meal = ''

        if date == '':
            date_obj = None

        else:
            err = False
            try:
                date_tok = date.split('/')
                date_obj = make_date(int(date_tok[2]),
                                     int(date_tok[0]),
                                     int(date_tok[1]))
            except Exception, e:
                errmes = 'Error: Incorrect date format. Correct format is MM/DD/YYYY.'
                err = True
            if err:
                return render_to_response('card/meals_list.html',
                                          {'club': club0,
                                           'memberID': memberID,
                                           'otherID': otherID,
                                           'oClub': oClub,
                                           'oChecker': iChecker,
                                           'status': status,
                                           'date': date,
                                           'meal': meal,
                                           'hostinc':None,
                                           'guestinc':None,
                                           'date_obj':None,
                                           'hostcomp':None,
                                           'guestcomp':None,
                                           'errmsg': errmsg})
    
    else:
        memberID = ''
        otherID = ''
        oClub = ''
        status = ''
        date = ''
        meal = ''
        date_obj = None
        oChecker = ''

    # hostM is every exchange "memberID" has started that fulfills above criteria
    if date_obj != None:
        hostM = Exchange.objects.filter(
            Q(meal_1__host__netid__icontains=memberID),
            Q(meal_1__guest__netid__icontains=otherID),
            Q(meal_1__guest__club__name__icontains=oClub),
            Q(meal_1__meal_type__icontains=meal)).filter(Q(meal_1__host__club=Cclub)).filter(Q(meal_1__date=date_obj) | Q(meal_2__date=date_obj)).filter(Q(meal_1__checker__netid__icontains=oChecker) | Q(meal_2__checker__netid__icontains=oChecker))
        
        # guestM is every exchange "otherID" was started that fulfills above criteria
        guestM = Exchange.objects.filter(
            Q(meal_1__host__netid__icontains=otherID),
            Q(meal_1__guest__netid__icontains=memberID),
            Q(meal_1__host__club__name__icontains=oClub),
            Q(meal_1__meal_type__icontains=meal)).filter(Q(meal_1__guest__club=Cclub)).filter(Q(meal_1__date=date_obj) | Q(meal_2__date=date_obj)).filter(Q(meal_1__checker__netid__icontains=oChecker) | Q(meal_2__checker__netid__icontains=oChecker))
        
    else:
        hostM = Exchange.objects.filter(
            Q(meal_1__host__netid__icontains=memberID),
            Q(meal_1__guest__netid__icontains=otherID),
            Q(meal_1__guest__club__name__icontains=oClub),
            Q(meal_1__meal_type__icontains=meal)).filter(Q(meal_1__host__club=Cclub)).filter(Q(meal_1__checker__netid__icontains=oChecker) | Q(meal_2__checker__netid__icontains=oChecker))
        
        guestM = Exchange.objects.filter(
            Q(meal_1__host__netid__icontains=otherID),
            Q(meal_1__guest__netid__icontains=memberID),
            Q(meal_1__host__club__name__icontains=oClub),
            Q(meal_1__meal_type__icontains=meal)).filter(Q(meal_1__guest__club=Cclub)).filter(Q(meal_1__checker__netid__icontains=oChecker) | Q(meal_2__checker__netid__icontains=oChecker))
        
    # hostinc is a subset of "hostM," where exchanges are incomplete
    if status == "complete":
        hostinc = None
    else:
        hostinc = list(hostM.filter(Q(meal_2=None)))

    # guestinc is a subset of "guestM," where exchanges are incomplete
    if status == "complete":
        guestinc = None
    else:
        guestinc = list(guestM.filter(Q(meal_2=None)))

    # hostcomp is a subset of "hostM," where exchanges are complete, and "memberID" started the exchange
    if status == "incomplete":
        hostcomp = None
    else:
        hostcomp = list(hostM.filter(Q(meal_2__isnull=False)))

    # guestcomp is a subset of "guestM," where exchanges are complete, and "otherID" started the exchange
    if status == "incomplete":
        guestcomp = None
    else:
        guestcomp = list(guestM.filter(Q(meal_2__isnull=False)))
    

    # TODO: Deactivate button (template)
    response = render_to_response('card/meals_list.html',
                                  {'club': club0,
                                   'memberID': memberID,
                                   'otherID': otherID,
                                   'oClub': oClub,
                                   'oChecker': oChecker,
                                   'status': status,
                                   'date': date,
                                   'meal': meal,
                                   'hostinc':hostinc,
                                   'guestinc':guestinc,
                                   'date_obj':date_obj,
                                   'hostcomp':hostcomp,
                                   'guestcomp':guestcomp,
                                   'errmsg': errmsg})
        
    return response 

def modMeals(request, club, mealid):
    """Renders the page for modifying meal data.""" 
    
    # Verify that the session is valid
    try:
        club0 = request.session['club']
    except:
        return redirect('/index/')
    if club0 != club:
        return redirect('/index/')

    meal = get_object_or_404(Meal, id=mealid)
    try:
        exchange = Exchange.objects.get(meal_2=meal)
    except:
        exchange = Exchange.objects.get(meal_1=meal)
    Cclub = get_object_or_404(Club, account__username=club0)
    msg = None
    errmes = None
    date_obj = None

    if request.method == 'POST':
        if 'Remove' in request.POST:
            form = AddMealForm(instance=meal)

            # Delete meal and remove from exchange
            try:
                removeFromExchange(meal)
                meal.delete()
            except:
                errmes = "Error: Could not remove meal."
                msg = None
                response = render_to_response('card/meals_mod.html',
                                              {'club': club,
                                               'meal': meal,
                                               'form':form,
                                               'mealid': mealid,
                                               'exchange':exchange,
                                               'date': date,
                                               'msg': msg,
                                               'errmes': errmes})
                return response    
        
            return redirect('/%s/meals/list/'%club)
        else:
            form = AddMealForm(request.POST, instance=meal)
            if form.is_valid():
                form.save()
                meal = form.instance
                try:
                    removeFromExchange(meal)
                    host = Member.objects.get(netid=meal.host.netid)
                    guest = Member.objects.get(netid=meal.guest.netid)
                    msg = makeexchange(Cclub.check,meal.meal_type,meal.host,meal.guest,meal.date, False)
                    meal.delete()
                    return redirect('/%s/meals/list/'%club)
                except Exception,e:
                    errmes = e
            else:
                errmes = "There were errors in this form"
    else:
        form = AddMealForm(instance=meal)

    return render_to_response('card/meals_mod.html',
                              {'club': club,
                               'mealid':mealid,
                               'form':form,
                               'errmes':errmes,
                               'msg': msg})


def removeFromExchange(meal):
    """Removes meal from its associated exchange object.

    This is a helper function for modMeals.  For simplicity,
    we remove the modified meal from the exchange, create a new
    meal, and find a new exchange for it."""
    
    secondMeal = Exchange.objects.filter(meal_2=meal)
    if secondMeal.count() != 0:
        for exchange in secondMeal:
            exchange.meal_2 = None
            exchange.save()
    else:
        firstMeal = Exchange.objects.filter(meal_1=meal)
        for exchange in firstMeal:
            if exchange.meal_2 != None:
                exchange.meal_1 = exchange.meal_2
                exchange.meal_2 = None
                exchange.save()
            else:
                exchange.delete()
    
def validateMeal(hostid, guestid, club, date, mealtype):
    if mealtype not in MEAL_CHOICES:
        return "Error: Not a valid meal type."
    
    # Validate host change
    try:
        host = Member.objects.get(netid=hostid)
    except:
        return "Error: Host netid does not exist in the system."
    # The club must remain involved in the exchange
    if club != host.club:
        return "Error: Host must be a member of "+ str(club.name) +"."

    # Validate guest change
    try:
        guest = Member.objects.get(netid=guestid)
    except:
        return "Error: Guest netid does not exist in the system."

    if club == guest.club:
        return "Error: Guest may not be a member of "+club+"."

    # validate date
    date_tok = date.split('/')
    now = make_date.today()
    if int(date_tok[2]) > int(now.year) or int(date_tok[2]) < 2000:
        return "Error: Incorrect Date Format. Correct Format is MM/DD/YYYY."

    return "Success"

def check_swipe_club(request,netid):
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
            return render_to_response('card/meals_add.html',
                                      {'errmes':'Error: Host is not registered with the system.',
                                       'onload':'select_elem()',
                                       'form':AddMealForm(),
                                       'today':datetime.today().strftime('%m/%d/%Y'),
                                       'club': club})
        try:
            g = Member.objects.get(puid=guest_puid)
            if not g.is_active:
                raise Exception
        except:
            return render_to_response('card/meals_add.html',
                                      {'errmes':'Error: Guest is not registered with the system.',
                                       'onload':'select_elem()',
                                       'form':AddMealForm(),
                                       'today':datetime.today().strftime('%m/%d/%Y'),
                                       'club': club})

        # Error checking
        if h == g:
            errmes = 'Error: host and guest cannot be the same.'
        elif h.club != checker.club:
            errmes = "Error: host and checker must be from the same club."

    if errmes:
        return render_to_response('card/meals_add.html',
                                  {'errmes': errmes,
                                   'form':AddMealForm(),
                                   'today':datetime.today().strftime('%m/%d/%Y'),
                                   'onload':'select_elem()',
                                   'club': club})
    else:
        return render_to_response('card/meals_add.html',
                                  {'host': h,
                                   'guest': g,
                                   'today':datetime.today().strftime('%m/%d/%Y'),
                                   'swiped':True,
                                   'form':AddMealForm(),
                                   'onload':'select_elem()',
                                   'club': club})
