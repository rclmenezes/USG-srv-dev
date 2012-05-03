from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, HttpResponseServerError
from django.template import RequestContext
from pom.models import *
import datetime
import simplejson

def index(request, offset):
    # not used due to direct_to_template in urls.py
    return render_to_response('pom/index.html', {}, RequestContext(context))



def getBldgsWithHours():
    pass

def getBldgsWithMenus():
    return ('WILCH', 'WUHAL', 'HAMIL', 'FORBC', 'HARGH', 'CENJL', 'GRADC')

def getBldgsWithLaundry():
    return ('WALKE', 'C1915', 'DICKH', 'BLAIR', 'BLOOM', 'BROWN', 'SCULL', 
                     'YOSEL', 'BUYER', 'ENOHA', 'DODHA', 'EDWAR', 'FEINB', 'FORBC', 
                     'HAMIL', 'HENRY', 'HOLDE', 'JOLIN', 'LITTL', 'LOCKH', 'CUYLE',
                     'PYNEH', 'SCULL', 'SPELM', 'HARGH')

def bldgs_for_filter(request):
    '''
    Return a JSON-list of building codes that should be highlighted given
    the filters in the GET parameters of the request.
    '''
    if 'type' not in request.GET:
        return HttpResponseServerError("No type in GET")
    
    filter_type = request.GET['type']
    if filter_type == '0': 
        events = Building.cal_events.date_filtered(request.GET['m0'], request.GET['d0'], request.GET['y0'], request.GET['h0'],
                                                   request.GET['m1'], request.GET['d1'], request.GET['y1'], request.GET['h1'])
        bldgsList = list(set((event.event_location for event in events)))
    #1 = hours
    elif filter_type == '1':
        bldgsList = getBldgsWithHours()
    #2 = menus
    elif filter_type == '2':
        bldgsList = getBldgsWithMenus()
    #3 = washing machines
    elif filter_type == '3':
        bldgsList = getBldgsWithLaundry()
        #html = {'events': [(event.event_location  + "info_sep" + event.event_cluster.cluster_title + "info_sep" + event.event_date_time_start.isoformat(' ') + "info_sep" + event.event_date_time_end.isoformat(' ')) for event in events]}
    else:#elif filter_type == '1':
        events = Building.cal_events.all()
        bldgsList = list(set((event.event_location for event in events)))
        
    response_json = simplejson.dumps({'error': None,
                                      'bldgs': bldgsList})
    return HttpResponse(response_json, content_type="application/javascript")


def events_for_bldg(request, bldg_code):
    '''
    Return the HTML that should be rendered in the info box given the
    building in the GET parameter of the request
    '''
    try:
        bldg = Building.objects.get(bldg_code=bldg_code)
        events = Building.cal_events.bldg_filtered(bldg)
        html = render_to_string('pom/event_info.html',
                         {'bldg_name': bldg.name,
                          'events': events})
        response_json = simplejson.dumps({'error': None,
                                          'html': html,
                                          'bldgId': bldg_code})
    except Exception, e:
        response_json = simplejson.dumps({'error': str(e)})
        
    return HttpResponse(response_json, content_type="application/javascript")

