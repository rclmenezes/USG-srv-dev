from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, HttpResponseServerError
from django.template import RequestContext
#from pom.models import *
from cal.models import Event
from pom import cal_event_query
from pom.bldg_info import *
import pom.campus_map_codes
import pom.campus_map_bldgs_info
from pom.menus import scraper as menus
from pom.printers import scraper as printers
from pom.laundry import scraper as laundry
import datetime, simplejson
from django.core.cache import cache
from django.core.mail import send_mail



# not used due to direct_to_template in urls.py
def index(request, offset):
    return render_to_response('pom/index.html', {}, RequestContext(context))


def get_bldg_names_json(request):
    '''
    make dictionary of name, code pairs for use in location-based filtering
    '''
    bldg_names = dict((name[0], code) for code, name in BLDG_INFO.iteritems())
    response_json = simplejson.dumps(bldg_names)
    return HttpResponse(response_json, content_type="application/javascript")

def get_cal_events_json(request, events_list=None):
    if not events_list:
        events_list = filter_cal_events(request)
    try:
        start_date = datetime.datetime(int(request.GET['y0'])-1, int(request.GET['m0']), int(request.GET['d0']))
        start_index = 2*int(request.GET['h0']) + round(int(request.GET['i0'])/30)
        end_index = 2*int(request.GET['h1']) + round(int(request.GET['i1'])/30)
        n_days = int(request.GET['nDays'])
    except Exception, e:
        raise Exception('Bad GET request: missing get params (%s)' % str(e))
    
    mark_data = {}
    events_data = {}
    for event in events_list:
        events_data[event.event_id] = event.event_location
        
        e_start = event.event_date_time_start
        delta = e_start - start_date
        half_hrs_delta = int(round(delta.total_seconds()/1800)) % 48
        time_index = str(delta.days) + '-' + str(half_hrs_delta)
        
        e_dict = {'bldgCode': event.event_location, 'eventId': event.event_id}
        #e_dict['startTime'] = e_start
        #e_dict['endTime'] = event.event_date_time_end
        
        if time_index in mark_data:
            mark_data[time_index].append(e_dict)
        else:
            mark_data[time_index] = [e_dict]
        
    return {'eventsData': events_data, 'markData': mark_data}



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
            response_dict = dict({'error': None, 'html': html, 'bldgCode': bldg_code}.items() + get_cal_events_json(request, events).items())
        except Exception, e:
            response_dict = {'error': str(e)}
        
        
    elif filter_type == '2': #menus        
        #assert building is a dining hall
        if bldg_code not in getBldgsWithMenus():
            err = 'requested menu info from invalid building ' + BLDG_INFO[bldg_code][0]
            response_json = simplejson.dumps({'error': err})
        else:
            try:
                menu_list = cache.get('menu_list')
                if menu_list == None:
                    menu_list = menus.scrape_all()
                    menu_list = list(set([(hall, menu) for hall, menu in menu_list.items()]))
                    menu_list = sorted(menu_list, key = lambda x: x[0])
                    for tup in menu_list:
                        tup[1].meals = [(name, meal) for name, meal in tup[1].meals.items()]
                        tup[1].meals = sorted(tup[1].meals, key = lambda x: menus_sorter(x[0]))
                    try:
                        cache.set('menu_list', menu_list, 1000)
                    except Exception, e:
                        send_mail('EXCEPTION IN pom.views events_for_bldg menus', e, 'from@example.com', ['nbal@princeton.edu', 'mcspedon@princeton.edu', 'ldiao@princeton.edu'], fail_silently=False)
                menu = dict(menu_list)[bldg_code]
                html = render_to_string('pom/menu_info.html',
                                        {'bldg_name': BLDG_INFO[bldg_code][0],
                                         'menu': menu})
                response_dict = {'error': None, 'html': html, 'bldgCode': bldg_code}
            except Exception, e:
                response_dict = {'error': str(e)}
    
    
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
                response_dict = {'error': None, 'html': html, 'bldgCode': bldg_code}
            except Exception, e:
                response_dict = {'error': str(e)}
    
    
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
                        send_mail('EXCEPTION IN pom.views events_for_bldg printing', e, 'from@example.com', ['nbal@princeton.edu', 'joshchen@princeton.edu', 'ldiao@princeton.edu'], fail_silently=False)
                printer_info = mapping[bldg_code]
                html = render_to_string('pom/printer_info.html',
                                        {'bldg_name': BLDG_INFO[bldg_code][0],
                                         'printers' : printer_info})
                response_dict = {'error': None, 'html': html, 'bldgCode': bldg_code}
            except Exception, e:
                response_dict = {'error': str(e)}
    
    elif filter_type == '5': #location
        try:
            codes = campus_map_codes.campus_map_codes[bldg_code]
            if codes[0] == 0: info = None
            else:
                info = [campus_map_bldgs_info.campus_map_info[code] for code in codes]

            html = render_to_string('pom/location_info.html',
                                    {'bldg_name':BLDG_INFO[bldg_code][0], 'info':info})
            response_dict = {'error': None, 'html': html, 'bldgCode': bldg_code}
        except Exception, e:
            response_dict = {'error': str(e)}
        
        
    else:
        raise Exception("Bad filter type in GET request: %s" % filter_type)
    
    
    response_json = simplejson.dumps(response_dict)
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
            response_json = simplejson.dumps(dict({'error': None, 'html': html}.items() + get_cal_events_json(request, events).items()))
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
                    tup[1].meals = sorted(tup[1].meals, key = lambda x: menus_sorter(x[0]))
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
    events = []
    try:
        if bldg_code:
            events = cal_event_query.filter_by_bldg(events, bldg_code)
        if 'search' in request.GET:
            events = cal_event_query.filter_by_search(events, request.GET['search'])
        if 'm0' in request.GET:
            start_day = datetime.date(int(request.GET['y0']), int(request.GET['m0']), int(request.GET['d0']))
            end_day = start_day + datetime.timedelta(days=int(request.GET['nDays']))
            events = cal_event_query.filter_by_day_hour(events,
                start_day.month, start_day.day, start_day.year, int(request.GET['h0']), int(request.GET['i0']),
                end_day.month, end_day.day, end_day.year, int(request.GET['h1']), int(request.GET['i1']))
        for event in events:
            desc = event.event_cluster.cluster_description
            event.short_desc = desc[:140]
            event.long_desc = desc[140:]
    except Exception, e:
        raise Exception('Bad GET request: '+ str(e))
    return events
     

def menus_sorter(name):
    x = {'Breakfast':0, 'Brunch':1, 'Lunch':2, 'Dinner':3}
    if name in x: return x[name]
    else:         return 4
#def filter_menus(request, bldg_code=None):
#    #TODO: could add filtering for just breakfast, etc based on request.GET here
#    #after the scrape but before the return
#    menu_list = cache.get('menu_list')
#    if bldg_code:
#        if menu_list:
#            return dict(menu_list)[bldg_code]
#        else:
#            menu = cache.get('menu_'+bldg_code)
#            if not menu:
#                menu = menus.scrape_single_menu(bldg_code)
#                menu.meals = [(name, meal) for name, meal in menu.meals.items()]
#                menu.meals = sorted(menu.meals, key = lambda x: menus_sorter(x[0]))
#                try: 
#                    cache.set('menu_'+bldg_code, menu, 1000)
#                except Exception, e:
#                    send_mail('EXCEPTION IN pom.views filter_menus1 menus', e, 'from@example.com', ['nbal@princeton.edu', 'joshchen@princeton.edu', 'ldiao@princeton.edu'], fail_silently=False)
#            return menu
#    if not menu_list:
#        menu_list = menus.scrape_all()
#        menu_list = [(hall, menu) for hall, menu in menu_list.items()]
#        menu_list = sorted(menu_list, key = lambda x: x[0])
#        for hall, menu in menu_list:
#            menu.meals = [(name, meal) for name, meal in menu.meals.iteritems()]
#            menu.meals = sorted(menu.meals, key = lambda x: menus_sorter(x[0]))
#        try: 
#            cache.set('menu_list', menu_list, 1000)
#        except Exception, e:
#            send_mail('EXCEPTION IN pom.views events_for_bldg menus', e, 'from@example.com', ['nbal@princeton.edu', 'joshchen@princeton.edu', 'ldiao@princeton.edu'], fail_silently=False)
#    return menu_list


def filter_laundry(request, bldg_code=None):
    #TODO: could add filtering for just breakfast, etc based on request.GET here
    #after the scrape but before the return
    machine_mapping = cache.get('laundry')
    if not machine_mapping:
        machine_mapping = laundry.scrape_all()
        try:
            cache.set('laundry', machine_mapping, 1000)
        except Exception, e:
            send_mail('EXCEPTION IN pom.views filter_laundry1', e, 'from@example.com', ['nbal@princeton.edu', 'joshchen@princeton.edu', 'ldiao@princeton.edu'], fail_silently=False)
            
    if bldg_code:
        return machine_mapping[bldg_code]
    machine_list = [x for k,v in machine_mapping.iteritems() for x in v]
    machine_list = sorted(machine_list, key=lambda x: x[0])
    return machine_list
    

#def filter_printers(request, bldg_code=None):
#    #TODO: could add filtering for just breakfast, etc based on request.GET here
#    #after the scrape but before the return
#    machine_mapping = cache.get('printer')
#    if not machine_mapping:
#        machine_mapping = printers.scrape_all()
#        try:
#            cache.set('printer', machine_mapping, 1000)
#        except Exception, e:
#            send_mail('EXCEPTION IN pom.views events_for_bldg printing', e, 'from@example.com', ['nbal@princeton.edu', 'joshchen@princeton.edu', 'ldiao@princeton.edu'], fail_silently=False)
#    
#    if bldg_code:
#        return machine_mapping[bldg_code]
#    printer_list = [(x.loc, x.color, x.status) for k,v in machine_mapping.iteritems() for x in v]
#    printer_list = sorted(printer_list, key=lambda x: x[0])
#    return printer_list





