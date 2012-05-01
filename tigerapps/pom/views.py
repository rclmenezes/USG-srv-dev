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



def bldgs_for_filter(request):
    '''
    Return a JSON-list of building codes that should be highlighted given
    the filters in the GET parameters of the request.
    '''
    if 'm0' in request.GET:
        events = Building.cal_events.date_filtered(request.GET['m0'], request.GET['d0'], request.GET['y0'], request.GET['h0'],
                                                   request.GET['m1'], request.GET['d1'], request.GET['y1'], request.GET['h1'])
        #html = {'events': [(event.event_location  + "info_sep" + event.event_cluster.cluster_title + "info_sep" + event.event_date_time_start.isoformat(' ') + "info_sep" + event.event_date_time_end.isoformat(' ')) for event in events]}
        response_json = simplejson.dumps({'error': None,
                                          'bldgs': list(set((event.event_location for event in events)))})
    elif 'hasLaundry' in request.GET:
        pass
    
    return HttpResponse(response_json, content_type="application/javascript")


def events_for_bldg(request, bldg_code):
    '''
    Return the HTML that should be rendered in the info box given the
    building in the GET parameter of the request
    '''
    try:
        bldg = Building.objects.get(bldg_code=bldg_code)
        events = Building.cal_events.all(bldg)
        html = render_to_string('pom/event_info.html',
                         {'bldg_name': bldg.name,
                          'events': events})
        response_json = simplejson.dumps({'error': None,
                                          'html': html,
                                          'bldgId': bldg_code})
    except Exception, e:
        response_json = simplejson.dumps({'error': str(e)})
        
    return HttpResponse(response_json, content_type="application/javascript")

