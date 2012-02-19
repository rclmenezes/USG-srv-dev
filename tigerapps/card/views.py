# -------------------------------------------------------------------#
# views.py                                                           #
# Written by Betina Evancha, Sarah Wellons, Michael Gordon, and      #
# Aaron Trippe                                                       #
# Description: View functions (unsorted or general).                 #
# -------------------------------------------------------------------#

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db.models import Q
from card.models import *
from checksession import *
from datetime import *

def index(request):
    """Renders the index page."""
    
#    if 'login_cas' in request.session and request.session['login_cas']:
#        logged_in = True
#    else:
#        logged_in = False
    response = render_to_response('card/index.html')
    return response

def personal(request, netid):
    """Renders the personal page for members.

    Searches for and displays all exchanges associated
    with the logged in user."""
    
    # Verify that the session is valid
    try:
        netid0 = request.session['netid']
    except:
        return redirect('/index/')
    if netid != netid0 or not request.session['login_cas']:
        return redirect('/index/')

    # Query the database for meals involving user
    completeExchanges = list(Exchange.objects.exclude(meal_2=None).filter(meal_1__host=netid))
    completeExchanges2 = list(Exchange.objects.exclude(meal_2=None).filter(meal_1__guest=netid))
    completeExchanges.extend(completeExchanges2) 
    hostExchanges = Exchange.objects.filter(meal_2=None, meal_1__host__netid=netid)
    guestExchanges = Exchange.objects.filter(meal_2=None, meal_1__guest__netid=netid)

    #days to expiration
    today = date.today()
    nextmonth = today.month+1
    if (today.month==12):
        year = today.year+1
    else:
        year = today.year
    expdate = date(month=nextmonth, day=1, year=year)
    days = (expdate-today).days - 1
    
    user = get_object_or_404(Member, netid=netid)
    role = user.access
         
    response = render_to_response('card/personal.html',
                                  {'netid': netid,
                                   'hostExchanges': hostExchanges,
                                   'guestExchanges': guestExchanges,
                                   'completeExchanges': completeExchanges,
                                   'role': role,
                                   'days': days})
    return response             
    
def help(request, path):
    #meta = request.META
    #if 'HTTP_REFERER' in meta:
        #prevpage = request.META['HTTP_REFERER']
    #else:
        #prevpage = "No previous page"
    #print prevpage
    if path == '':
        target = 'card/index_help.html'
    elif path[len(path)-1] == '/':
        target = "card/" + path[0:len(path)-1]+'_help.html'
    else:
        target = "card/" + path+'_help.html'
    return render_to_response(target)
                              #{'prevpage':prevpage})
