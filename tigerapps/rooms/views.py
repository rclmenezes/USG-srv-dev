# Create your views here.
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response
from dsml import gdi
# from rooms.models import Poll
from django.contrib.auth.decorators import login_required, user_passes_test
from models import *
from views import *
from django.core.urlresolvers import reverse
from django import forms
import json
import sys

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
    
@login_required
def update_queue(request, drawid):
    user = check_undergraduate(request.user.username)
    if not user:
        return HttpResponseForbidden()
    draw = Draw.objects.get(pk=drawid)
    qlist = json.loads(request.POST['queue'])
    # resp = ''
    # for r in qlist:
    #     resp += ' ' + r;
    queue = user.queues.filter(draw=draw)[0]
    if not queue:
        return HttpResponse('no queue')
    rooms = []
    for roomid in qlist:
        room = Room.objects.get(pk=roomid)
        if (not room) or not draw in room.building.draw.all():
            return HttpResponse('bad room/draw')
        rooms.append(room)
    # Clear out the old list
    queue.queuetoroom_set.all().delete()
    # Put in new relationships
    for i in range(0, len(rooms)):
        qtr = QueueToRoom(queue=queue, room=rooms[i], ranking=i)
        qtr.save()
    # Test output - list rooms
    return HttpResponse(rooms)

# Ajax for displaying this user's queue
@login_required
def get_queue(request, drawid):
    user = check_undergraduate(request.user.username)
    if not user:
        return HttpResponseForbidden()
    try:
        queue = user.queues.get(draw__id=drawid)
    except:
        return HttpResponse('no queue')
    queueToRooms = QueueToRoom.objects.filter(queue=queue).order_by('ranking')
    if not queueToRooms:
        return HttpResponse('no rooms')
    room_list = []
    for qtr in queueToRooms:
        room_list.append(qtr.room)
    return render_to_response('rooms/queue.html', {'room_list':room_list})

@login_required
#for testing
def review(request, roomid):
    if request.method == 'POST':
        cancel = request.POST.get('cancel', None)
        review = request.POST.get('review', None)
        submit = request.POST.get('submit', None)
        display = request.POST.get('display', None)
        
        if cancel:
            return HttpResponseRedirect(reverse(index))	#redirects to the view index
        if review:
            form = ReviewForm()
            return render_to_response('rooms/reviewtest.html', {'form': form, 'submitted': False})
        if display:
            revs = Review.objects.filter(room=Room.objects.filter(id=roomid))
            print 'num reviews found: %d' % (len(revs))
            return render_to_response('rooms/reviewtest.html', {'reviews': revs, 'display': display})
        if submit:
            form = ReviewForm(request.POST)
            if form.is_valid():
                print 'ok valid'
                rev = form.save(commit=False)
                rev.user = check_undergraduate(request.user)
                room = Room.objects.filter(id=roomid)
                if len(room) == 0:
                    return render_to_response('rooms/reviewtest.html', {'form': form, 'submitted': True, 'error': 'Invalid Room'})
                else:
                    rev.room = room[0]
                    rev.save()
                    return render_to_response('rooms/reviewtest.html', {'form': form, 'submitted': True})
            else:
                form = ReviewForm()
                return render_to_response('rooms/reviewtest.html', {'form': form, 'submitted': True, 'error': 'Invalid submit data'})
    else:
        return render_to_response('rooms/reviewtest.html', {'submitted': False})
