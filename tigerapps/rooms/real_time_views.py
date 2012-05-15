from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from dsml import gdi
# from rooms.models import Poll
from django.contrib.auth.decorators import login_required, user_passes_test
from models import *
from views import *
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django import forms
import json
import sys,os
import traceback

from simulation import start_sim, stop_sim, check_avail
from queue import *


REAL_TIME_ADDR='http://dev.rooms.tigerapps.org:8031'
NORMAL_ADDR='http://dev.rooms.tigerapps.org'
BASE_DOMAIN='rooms.tigerapps.org'

def externalResponse(data):
    response =  HttpResponse(data)
    response['Access-Control-Allow-Origin'] =  NORMAL_ADDR
    response['Access-Control-Allow-Credentials'] =  "true"
    return response


def externalize(request, response):
    response['Access-Control-Allow-Credentials'] =  "true"
    response['Access-Control-Allow-Origin'] = NORMAL_ADDR
    if 'HTTP_ORIGIN' in request.META:
        origin = request.META['HTTP_ORIGIN']
        if origin.find(BASE_DOMAIN) != -1:
            response['Access-Control-Allow-Origin'] = origin
    return response

def check_undergraduate(username):
    # Check if user can be here
    try:
        user = User.objects.get(netid=username)
    except:
        info = gdi(username)
        user = User(netid=username, firstname=info.get('givenName'), lastname=info.get('sn'), pustatus=info.get('pustatus'))
        if info.get('puclassyear'):
            user.puclassyear = int(info.get('puclassyear'))
        if user.pustatus == 'undergraduate' and 2011 < user.puclassyear:
            user.save()
            #Create queues for each draw
            for draw in Draw.objects.all():
                queue = Queue(draw=draw)
                queue.save()
                user.queues.add(queue)
    if user.pustatus == 'undergraduate' and 2011 < user.puclassyear:
        return user
    return None


##################
# Real-time view functions go here (long polling)
    
@login_required
def update_queue(request, drawid):
    user = check_undergraduate(request.user.username)
    if not user:
        return externalResponse('forbidden')
    draw = Draw.objects.get(pk=drawid)
    qlist = json.loads(request.POST['queue'])
    # resp = ''
    # for r in qlist:
    #     resp += ' ' + r;
    queue = user.queues.filter(draw=draw)[0]
    if not queue:
        return externalResponse('no queue')

    # QueueManager object takes over
    # rooms = []
    # for roomid in qlist:
    #     room = Room.objects.get(pk=roomid)
    #     if (not room) or not draw in room.building.draw.all():
    #         return externalResponse('bad room/draw')
    #     rooms.append(room)
    # # Clear out the old list
    # queue.queuetoroom_set.all().delete()
    # # Put in new relationships
    # for i in range(0, len(rooms)):
    #     qtr = QueueToRoom(queue=queue, room=rooms[i], ranking=i)
    #     qtr.save()
    # # Test output - list rooms
    # return externalResponse(rooms)
    try:
        return externalize(request, edit(user, queue, qlist, draw))
    except Exception as e:
        return externalResponse(e)

# Ajax for displaying this user's queue
@login_required
def get_queue(request, drawid, timestamp = 0):
    user = check_undergraduate(request.user.username)
    timestamp = int(timestamp)
    if not user:
        return externalResponse('no user')
    try:
        draw = Draw.objects.get(pk=drawid)
        queue = user.queues.get(draw=draw)
    except Exception as e:
        return externalResponse(traceback.format_exc(2) + str(draw))
    #real-time takes over
#    return externalResponse(queue)
    try:
        return externalize(request, check(user, queue, timestamp))
    except Exception as e:
        return externalResponse(traceback.format_exc(2))
    

    # queueToRooms = QueueToRoom.objects.filter(queue=queue).order_by('ranking')
    # if not queueToRooms:
    #     return HttpResponse('')
    # room_list = []
    # for qtr in queueToRooms:
    #     room_list.append(qtr.room)
    # return render_to_response('rooms/queue.html', {'room_list':room_list})


def start_simulation(request, delay, size=1):
    delay = int(delay)
    size = int(size)
    return start_sim(delay, size)

def stop_simulation(request):
    return stop_sim()

def check_availability(request, timestamp):
    return externalize(request, check_avail(int(timestamp)))
