from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, HttpResponseServerError
from django.template import RequestContext
#from pom.models import *
from pom.bldg_codes import *
from pom import cal_event_query
import datetime, simplejson

def index(request, offset):
    # not used due to direct_to_template in urls.py
    return render_to_response('pom/index.html', {}, RequestContext(context))


def bldgs_for_filter(request):
    '''
    Return a JSON-list of building codes that should be highlighted given
    the filters in the GET parameters of the request.
    '''
    if 'type' not in request.GET:
        return HttpResponseServerError("No type in GET")
    
    filter_type = request.GET['type']
    if filter_type == '0': 
        events = cal_event_query.date_filtered(request.GET['m0'], request.GET['d0'], request.GET['y0'], request.GET['h0'],
                                                  request.GET['m1'], request.GET['d1'], request.GET['y1'], request.GET['h1'])
        bldgsList = list(set((event.event_location for event in events)))
    
    elif filter_type == '1':
        #1 = hours
        bldgsList = getBldgsWithHours()
    
    elif filter_type == '2':
        #2 = menus
        bldgsList = getBldgsWithMenus()
    
    elif filter_type == '3':
        #3 = laundry
        bldgsList = getBldgsWithLaundry()
        #html = {'events': [(event.event_location  + "info_sep" + event.event_cluster.cluster_title + "info_sep" + event.event_date_time_start.isoformat(' ') + "info_sep" + event.event_date_time_end.isoformat(' ')) for event in events]}
    
    elif filter_type == '4':
        #4 = printers
        bldgsList = getBldgsWithPrinters()
        
    else:
        #Let an error happen, since this shouldn't occur
        pass
        
    response_json = simplejson.dumps({'error': None,
                                      'bldgs': tuple(bldgsList)})
    return HttpResponse(response_json, content_type="application/javascript")



def events_for_bldg(request, bldg_code):
    '''
    Return the HTML that should be rendered in the info box given the
    building in the GET parameter of the request
    '''
    try:
        events = cal_event_query.bldg_filtered(bldg_code)
        html = render_to_string('pom/event_info.html',
                                {'bldg_name': BLDG_INFO[bldg_code][0],
                                 'events': events})
        response_json = simplejson.dumps({'error': None,
                                          'html': html,
                                          'bldgId': bldg_code})
    except Exception, e:
        response_json = simplejson.dumps({'error': str(e)})
        
    return HttpResponse(response_json, content_type="application/javascript")


