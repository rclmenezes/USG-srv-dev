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


def get_bldg_names_json(request):
    '''
    make dictionary of name, code pairs for use in location-based filtering
    '''
    bldg_names = dict((name[0], code) for code, name in BLDG_INFO.iteritems())
    response_json = simplejson.dumps(bldg_names)
    return HttpResponse(response_json, content_type="application/javascript")

def get_cal_events_json(request):
    events_list = filter_cal_events(request)
    events_dict = {}
    for event in events_list:
        e_dict = {}
        e_dict['startTime'] = event.event_date_time_start
        e_dict['endTime'] = event.event_date_time_end
        e_dict['bldg_code'] = event.event_location
        events_dict[event.event_id] = e_dict
        
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
    response_json = json.dumps(events_dict, default=dthandler)
    return HttpResponse(response_json, content_type="application/javascript")



def bldgs_for_filter(request):
    '''
    Return a JSON-list of building codes that should be highlighted given
    the filters in the GET parameters of the request.
    '''
    if 'type' not in request.GET:
        return HttpResponseServerError("No type in GET")
    filter_type = request.GET['type']

    if filter_type == '0': #standard event
        events = filter_cal_events(request)
        bldgsList = list(set((event.event_location for event in events)))
        
    elif filter_type == '2': #menus
        bldgsList = getBldgsWithMenus()
    
    elif filter_type == '3': #laundry
        bldgsList = getBldgsWithLaundry()
    
    elif filter_type == '4': #printers
        bldgsList = getBldgsWithPrinters()
        
    else:
        raise Exception("Bad filter type in GET request: %s" % filter_type)
        
    response_json = simplejson.dumps({'error': None,
                                      'bldgs': tuple(bldgsList)})
    return HttpResponse(response_json, content_type="application/javascript")



def sorting_func(val):
    if (val == 'Breakfast'):
        return 0
    elif (val == 'Brunch'):
        return 1
    elif (val == 'Lunch'):
        return 2
    else:
        return 3

def events_for_bldg(request, bldg_code):
    '''
    Return the HTML that should be rendered in the info box given the
    building in the GET parameter of the request
    '''
    if 'type' not in request.GET:
        return HttpResponseServerError("No type in GET")
    filter_type = request.GET['type']
    
    
    if filter_type == '0': #standard event
        try:
            events = filter_cal_events(request, bldg_code)
            html = render_to_string('pom/event_info.html',
                                    {'bldg_name': BLDG_INFO[bldg_code][0],
                                     'events': events})
            response_json = simplejson.dumps({'error': None,
                                              'html': html,
                                              'bldgCode': bldg_code})
        except Exception, e:
            response_json = simplejson.dumps({'error': str(e)})
        
        
    elif filter_type == '2': #menus        
        #assert building is a dining hall
        if bldg_code not in getBldgsWithMenus():
           err = 'requested menu info from invalid building ' + BLDG_INFO[bldg_code][0]
           response_json = simplejson.dumps({'error': err})
        else:
            try:
                log = open('/srv/tigerapps/slog','a')
                log.write('before call to scrape: %s\n' % bldg_code)
                log.close()
                menu_list = cache.get('menu_list') 
                if menu_list == None:
                    menu_list = menus.scrape_all()
                    menu_list = list(set([(hall, menu) for hall, menu in menu_list.items()]))
                    menu_list = sorted(menu_list, key = lambda x: x[0])
                    for tup in menu_list:
                        tup[1].meals = [(name, meal) for name, meal in tup[1].meals.items()]
                        tup[1].meals = sorted(tup[1].meals, key = lambda x: sorting_func(x[0]))
                    try: 
                        cache.set('menu_list', menu_list, 1000)
                    except Exception, e:
                        send_mail('EXCEPTION IN pom.views events_for_bldg menus', e, 'from@example.com', ['nbal@princeton.edu', 'mcspedon@princeton.edu', 'ldiao@princeton.edu'], fail_silently=False)
                                        
                menu = ''
                for x in menu_list:
                    if x[0] == bldg_code:
                        menu = x[1]
                        break
                
                html = render_to_string('pom/menu_info.html',
                                        {'bldg_name': BLDG_INFO[bldg_code][0],
                                         'menu': menu})
                response_json = simplejson.dumps({'error': None,
                                                  'html': html,
                                                  'bldgCode': bldg_code})
            except Exception, e:
                response_json = simplejson.dumps({'error': str(e)})
    
    
    elif filter_type == '3': #laundry
        #assert building contains laundry room
        if bldg_code not in getBldgsWithLaundry():
           err = 'requested laundry info from invalid building ' + BLDG_INFO[bldg_code][0]
           response_json = simplejson.dumps({'error': err})
        else:
            try:
                machine_list_bldg = filter_laundry(request, bldg_code)
                html = render_to_string('pom/laundry_info.html',
                                        {'bldg_name': BLDG_INFO[bldg_code][0],
                                         'machines' : machine_list_bldg})
                response_json = simplejson.dumps({'error': None,
                                                  'html': html,
                                                  'bldgCode': bldg_code})
            except Exception, e:
                response_json = simplejson.dumps({'error': str(e)}) 
    
    
    elif filter_type == '4': #printers
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
        raise Exception("Bad filter type in GET request: %s" % filter_type)
            

    return HttpResponse(response_json, content_type="application/javascript")



def events_for_all_bldgs(request):
    '''
    Return the HTML that should be rendered in the info box given the
    building in the GET parameter of the request
    '''
    if 'type' not in request.GET:
        return HttpResponseServerError("No type in GET")
    filter_type = request.GET['type']
    
    
    if filter_type == '0': #standard event
        try:
            events = filter_cal_events(request)
            html = render_to_string('pom/event_info.html',
                                    {'bldg_name': 'All Events',
                                     'events': events})
            response_json = simplejson.dumps({'error': None,
                                              'html': html})
        except Exception, e:
            response_json = simplejson.dumps({'error': str(e)})
    
            
    elif filter_type == '2': #menus
        try:
            menu_list = cache.get('menu_list') 
            if menu_list == None:
                menu_list = menus.scrape_all()
                menu_list = list(set([(hall, menu) for hall, menu in menu_list.items()]))
                menu_list = sorted(menu_list, key = lambda x: x[0])
                for tup in menu_list:
                    tup[1].meals = [(name, meal) for name, meal in tup[1].meals.items()]
                    tup[1].meals = sorted(tup[1].meals, key = lambda x: sorting_func(x[0]))
                try: 
                    cache.set('menu_list', menu_list, 1000)
                except Exception, e:
                    send_mail('EXCEPTION IN pom.views events_for_bldg menus', e, 'from@example.com', ['nbal@princeton.edu', 'mcspedon@princeton.edu', 'ldiao@princeton.edu'], fail_silently=False)
            
            html = render_to_string('pom/menu_info_all.html',
                                    {'menu_list': menu_list,
                                     'bldg_info': BLDG_INFO})
            response_json = simplejson.dumps({'error': None,
                                              'html': html})
        except Exception, e:
            response_json = simplejson.dumps({'error': str(e)})
   
    
    elif filter_type == '3': #laundry
        try:
            machine_list = filter_laundry(request)
            html = render_to_string('pom/laundry_info_all.html',
                                    {'machine_list' : machine_list})
            response_json = simplejson.dumps({'error': None,
                                              'html': html})
        except Exception, e:
            response_json = simplejson.dumps({'error': str(e)}) 
    
    
    elif filter_type == '4': #printers
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
                    cache.set('printer', mapping, 1000)
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
        raise Exception("Bad filter type in GET request: %s" % filter_type)
    
        
    return HttpResponse(response_json, content_type="application/javascript")



####
#Helper functions for views above
####

def filter_cal_events(request, bldg_code=None):
    events = None
    if 'm0' in request.GET:
        events = cal_event_query.filter_by_date(events,
            request.GET['m0'], request.GET['d0'], request.GET['y0'], request.GET['h0'],
            request.GET['m1'], request.GET['d1'], request.GET['y1'], request.GET['h1'])
    if 'search' in request.GET:
        events = cal_event_query.filter_by_search(events, request.GET['search'])
    if bldg_code:
        events = cal_event_query.filter_by_bldg(events, bldg_code)
    return events


def filter_menus(request, bldg_code=None):
    #TODO: could add filtering for just breakfast, etc based on request.GET here
    #after the scrape but before the return
    log = open('/srv/tigerapps/slog','a')
    log.write('before call to scrape: %s\n' % bldg_code)
    log.close()
    menu_list = cache.get('menu_list')
    if not menu_list:
        if bldg_code:
            menu = cache.get('menu_'+bldg_code)
            if not menu:
                menu = scrape_single_menu(bldg_code)
            try: 
                cache.set('menu_'+bldg_code, menu, 1000)
            except Exception, e:
                send_mail('EXCEPTION IN pom.views filter_menus1 menus', e, 'from@example.com', ['nbal@princeton.edu', 'mcspedon@princeton.edu', 'ldiao@princeton.edu'], fail_silently=False)
            return menu
        else:
            menu_list = menus.scrape_all()
            try: 
                cache.set('menu_list', menu_list, 1000)
            except Exception, e:
                send_mail('EXCEPTION IN pom.views filter_menus2 menus', e, 'from@example.com', ['nbal@princeton.edu', 'mcspedon@princeton.edu', 'ldiao@princeton.edu'], fail_silently=False)
    if bldg_code:
        return menu_list[bldg_code]
    return menu_list


def filter_laundry(request, bldg_code=None):
    #TODO: could add filtering for just breakfast, etc based on request.GET here
    #after the scrape but before the return
    mapping = cache.get('laundry')
    if not mapping:
        mapping = laundry.scrape_all()
        try:
            cache.set('laundry', mapping, 1000)
        except Exception, e:
            send_mail('EXCEPTION IN pom.views filter_laundry1', e, 'from@example.com', ['nbal@princeton.edu', 'mcspedon@princeton.edu', 'ldiao@princeton.edu'], fail_silently=False)
    if bldg_code:
        return mapping[bldg_code]
    
    machine_list = cache.get('laundry_list')
    if not machine_list: 
        machine_list = [x for k,v in mapping.items() for x in v]
        machine_list = sorted(machine_list, key=lambda x: x[0])
        try: 
            cache.set('laundry_list', machine_list, 1000)
        except Exception, e:
            send_mail('EXCEPTION IN pom.views filter_laundry2', e, 'from@example.com', ['nbal@princeton.edu', 'mcspedon@princeton.edu', 'ldiao@princeton.edu'], fail_silently=False)
    return machine_list



