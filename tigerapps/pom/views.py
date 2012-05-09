from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, HttpResponseServerError
from django.template import RequestContext
#from pom.models import *
from cal.models import Event
from pom import cal_event_query
from pom.bldg_info import *
from pom.menus import scraper as menus
from pom.printers import scraper as printers
from pom.laundry import scraper as laundry
import datetime, simplejson
from django.core.cache import cache
from django.core.mail import send_mail

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
        #0 = standard event
        events = cal_event_query.date_filtered(request.GET['m0'], request.GET['d0'], request.GET['y0'], request.GET['h0'],
                                                  request.GET['m1'], request.GET['d1'], request.GET['y1'], request.GET['h1'])
        bldgsList = list(set((event.event_location for event in events)))
    
    elif filter_type == '1':
        #1 = hours
        #bldgsList = getBldgsWithHours()
        raise Exception('Not implemented')
    
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
    if 'type' not in request.GET:
        return HttpResponseServerError("No type in GET")
    filter_type = request.GET['type']
    
    if filter_type == '0':
        #0 = standard event
        try:
            events = cal_event_query.filter_res_by_date(cal_event_query.bldg_filtered(bldg_code), 
                                                        request.GET['m0'], request.GET['d0'], request.GET['y0'], request.GET['h0'],
                                                        request.GET['m1'], request.GET['d1'], request.GET['y1'], request.GET['h1'])
            html = render_to_string('pom/event_info.html',
                                    {'bldg_name': BLDG_INFO[bldg_code][0],
                                     'events': events})
            response_json = simplejson.dumps({'error': None,
                                              'html': html,
                                              'bldgCode': bldg_code})
        except Exception, e:
            response_json = simplejson.dumps({'error': str(e)})
    
    
    elif filter_type == '1':
        #1 = hours
       
        #assert building is one for which we scrape hours
        #if bldg_code not in getBldgsWithHours():
        #   err = 'requested hours info for invalid building ' + BLDG_INFO[bldg_code][0]
        #   response_json = simplejson.dumps({'error': err})
        #else:
        #    try:
        #        hours = get_bldg_hours(bldg_code)
        #        html = render_to_string('pom/hours_info.html',
        #                                {'bldg_name': BLDG_INFO[bldg_code][0],
        #                                 'hours': hours})
        #        response_json = simplejson.dumps({'error': None,
        #                                          'html': html,
        #                                          'bldgCode': bldg_code})
        #    except Exception, e:
        #        response_json = simplejson.dumps({'error': str(e)})
        raise Exception('Not implemented')
        
        
    elif filter_type == '2':
        #2 = menus
        
        #assert building is a dining hall
#        if bldg_code not in getBldgsWithMenus():
#           err = 'requested menu info from invalid building ' + BLDG_INFO[bldg_code][0]
#           response_json = simplejson.dumps({'error': err})
#        else:
#            try:
#                log = open('/srv/tigerapps/slog','a')
#                log.write('before call to scrape: %s\n' % bldg_code)
#                log.close()
#                menu_info = menus.scrape_single_menu(bldg_code)
#                html = render_to_string('pom/menu_info.html',
#                                        {'bldg_name': BLDG_INFO[bldg_code][0],
#                                         'menu': menu_info})
#                response_json = simplejson.dumps({'error': None,
#                                                  'html': html,
#                                                  'bldgCode': bldg_code})
#            except Exception, e:
#                response_json = simplejson.dumps({'error': str(e)})
        raise Exception('Not implemented')
    
    
    elif filter_type == '3':
        #3 = laundry
    
        #assert building contains laundry room
        response_json = simplejson.dumps({'error': 'not implemented'})

        if bldg_code not in getBldgsWithLaundry():
           err = 'requested laundry info from invalid building ' + BLDG_INFO[bldg_code][0]
           response_json = simplejson.dumps({'error': err})
        else:
            try:
                mapping = cache.get('laundry')
                if mapping == None:
                    mapping = laundry.scrape_all()
                    try: 
                        cache.set('laundry', mapping, 1000)
                    except Exception, e:
                        send_mail('EXCEPTION IN pom.views events_for_bldg laundry', e, 'from@example.com', ['nbal@princeton.edu', 'mcspedon@princeton.edu', 'ldiao@princeton.edu'], fail_silently=False)
                laundry_info = mapping[bldg_code]
                html = render_to_string('pom/laundry_info.html',
                                        {'bldg_name': BLDG_INFO[bldg_code][0],
                                         'machines' : laundry_info})
                response_json = simplejson.dumps({'error': None,
                                                  'html': html,
                                                  'bldgCode': bldg_code})
            except Exception, e:
                response_json = simplejson.dumps({'error': str(e)}) 
    
    
    elif filter_type == '4':
        #4 = printers

        #assert building contains printer
        if bldg_code not in getBldgsWithPrinters():
           err = 'requested printer info from invalid building ' + BLDG_INFO[bldg_code][0]
           response_json = simplejson.dumps({'error': err})
        else:
            try:
                mapping = cache.get('printer')
                if mapping == None:
                    mapping = printers.scrape_all()
                    try:
                        cache.set('printer', mapping, 1000)
                    except Exception, e:
                        send_mail('EXCEPTION IN pom.views events_for_bldg printing', e, 'from@example.com', ['nbal@princeton.edu', 'mcspedon@princeton.edu', 'ldiao@princeton.edu'], fail_silently=False)
                printer_info = mapping[bldg_code]
                html = render_to_string('pom/printer_info.html',
                                        {'bldg_name': BLDG_INFO[bldg_code][0],
                                         'printers' : printer_info})
                response_json = simplejson.dumps({'error': None,
                                                  'html': html,
                                                  'bldgCode': bldg_code})
            except Exception, e:
                response_json = simplejson.dumps({'error': str(e)})
        
        
    else:
        #Let an error happen, since this shouldn't occur
        pass
            

    return HttpResponse(response_json, content_type="application/javascript")


def events_for_all_bldgs(request):
    '''
    Return the HTML that should be rendered in the info box given the
    building in the GET parameter of the request
    '''
    if 'type' not in request.GET:
        return HttpResponseServerError("No type in GET")
    filter_type = request.GET['type']
    
    if filter_type == '0':
        #0 = standard event
        try:
            events = cal_event_query.date_filtered(request.GET['m0'], request.GET['d0'], request.GET['y0'], request.GET['h0'],
                                                        request.GET['m1'], request.GET['d1'], request.GET['y1'], request.GET['h1'])
            html = render_to_string('pom/event_info_all.html',
                                    {'bldg_name': 'All Events',
                                     'events': events})
            response_json = simplejson.dumps({'error': None,
                                              'html': html})
        except Exception, e:
            response_json = simplejson.dumps({'error': str(e)})
    
            
    elif filter_type == '2':
        #2 = menus
        
        #assert building is a dining hall
        if bldg_code not in getBldgsWithMenus():
           err = 'requested menu info from invalid building ' + BLDG_INFO[bldg_code][0]
           response_json = simplejson.dumps({'error': err})
        else:
            try:
                menu_info = menus.scrape_single_menu(bldg_code)
                html = render_to_string('pom/menu_info.html',
                                        {'bldg_name': BLDG_INFO[bldg_code][0],
                                         'menu': menu_info})
                response_json = simplejson.dumps({'error': None,
                                                  'html': html,
                                                  'bldgCode': bldg_code})
            except Exception, e:
                response_json = simplejson.dumps({'error': str(e)})  
    
    
    elif filter_type == '3':
        #3 = laundry
    
        #assert building contains laundry room
        
        try:
            machine_list = cache.get('laundry_list')
            if machine_list == None:
                mapping = laundry.scrape_all()
                machine_list = []
                for key, value in mapping.items():
                    for x in value:
                        machine_list.append(x)
                machine_list = sorted(machine_list, key=lambda x: x[0])
                try: 
                    cache.set('laundry_list', machine_list, 1000)
                except Exception, e:
                    send_mail('EXCEPTION IN pom.views events_for_bldg laundry', e, 'from@example.com', ['nbal@princeton.edu', 'mcspedon@princeton.edu', 'ldiao@princeton.edu'], fail_silently=False)
            
            
            html = render_to_string('pom/laundry_info_all.html',
                                    {'machine_list' : machine_list})
            response_json = simplejson.dumps({'error': None,
                                              'html': html})
        except Exception, e:
            response_json = simplejson.dumps({'error': str(e)}) 
    
    
    elif filter_type == '4':
        #4 = printers

        #assert building contains printer
        
        try:
            printer_list = cache.get('printer_list')
            if printer_list == None:
                mapping = printers.scrape_all()
                printer_list = []
                for key, value in mapping.items():
                    for x in value:
                        printer_list.append((x.loc, x.color, x.status))
                printer_list = sorted(printer_list, key=lambda x: x[0])
                try:
                    cache.set('printer_list', printer_list, 1000)
                except Exception, e:
                    send_mail('EXCEPTION IN pom.views events_for_bldg printing', e, 'from@example.com', ['nbal@princeton.edu', 'mcspedon@princeton.edu', 'ldiao@princeton.edu'], fail_silently=False)

            html = render_to_string('pom/printer_info_all.html',
                                    {'bldg_name': BLDG_INFO['FRIST'][0],
                                     'printers' : printer_list})
            response_json = simplejson.dumps({'error': None,
                                              'html': html})
        except Exception, e:
            response_json = simplejson.dumps({'error': str(e)})
        
        
    else:
        #Let an error happen, since this shouldn't occur
        pass
        
    return HttpResponse(response_json, content_type="application/javascript")


# make dictionary of name, code pairs for use in location-based filtering 
def make_bldg_names_json(request):
    bldg_names = dict((name[0], code) for code, name in BLDG_INFO.iteritems())
    response_json = simplejson.dumps(bldg_names)
    return HttpResponse(response_json, content_type="application/javascript")

