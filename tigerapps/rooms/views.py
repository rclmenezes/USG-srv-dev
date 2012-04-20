# Create your views here.
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render_to_response
from dsml import gdi
# from rooms.models import Poll
from django.contrib.auth.decorators import login_required, user_passes_test
from models import Draw, Building, Room, User, Queue
import json

def check_undergraduate(username):
    # Check if user can be here
    try:
        user = User.objects.get(netid=username)
    except:
        info = gdi(username)
        user = User(netid=username, firstname=info.get('givenName'), lastname=info.get('sn'), pustatus=info.get('pustatus'))
        if info.get('puclassyear'):
            user.puclassyear = int(info.get('puclassyear'))
        user.save()
    if user.pustatus == 'undergraduate' and 2011 < user.puclassyear:
        return user
    return None

@login_required
def index(request):
    draw_list = Draw.objects.order_by('id')
    mapscript = mapdata()
#    return HttpResponse(request.user.username);
    user = check_undergraduate(request.user.username)
    if not user:
        return HttpResponseForbidden()
    return render_to_response('rooms/base_dataPanel.html', locals())

@login_required
def draw(request, drawid):
    room_list = Room.objects.filter(building__draw__id=drawid)
    return render_to_response('rooms/drawtab.html', locals())

def mapdata():
    buildings = Building.objects.order_by('id')
    maplist = []
    for building in buildings:
        draws = []
        for draw in building.draw.all():
            draws.append(draw.id)
        maplist.append({'name':building.name, 'draws':draws,
                        'lat':building.lat, 'lon':building.lon})
    mapstring = json.dumps(maplist)
    mapscript = '<script type="text/javascript">mapdata = %s</script>' % mapstring
    return mapscript

@login_required
def create_queue(request, drawid):
    user = check_undergraduate(request.user.username)
    if not user:
        return HttpResponseForbidden()
    draw = Draw.objects.get(pk=drawid)
    # Check if user already has queue for this draw
    if user.queues.filter(draw=draw):
        return HttpResponse("fail")
    queue = Queue(draw=draw)
    queue.save()
    user.queues.add(queue)
    return HttpResponse("pass")
    
def update_queue(request, drawid):
    return HttpResponse("pass")
