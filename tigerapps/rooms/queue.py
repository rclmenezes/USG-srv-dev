import time
from rooms.models import *
from gevent.event import Event
import subprocess
import os, sys
import simplejson
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404

init_time = int(time.time())

timing_event = Event()

# Start the real-time server if need be
# if not 'IS_REAL_TIME_SERVER' in os.environ:
#     scriptname = 'serverscript.py'
#     scriptloc = os.path.dirname(__file__)+'/serverscript.py'
    
#     #os.environ['IS_REAL_TIME_SERVER'] = 'TRUE'
#     subprocess.Popen(scriptloc, close_fds=True)
#     #del os.environ['IS_REAL_TIME_SERVER']

NORMAL_ADDR='http://dev.rooms.tigerapps.org:8017'
# def externalResponse(data):
#     response =  HttpResponse(data)
#     response['Access-Control-Allow-Origin'] =  NORMAL_ADDR
#     response['Access-Control-Allow-Credentials'] =  "true"
#     response['Access-Control-Allow-Methods'] =  "JSON"
#     return response

def triggertime():
    timing_event.set()
    timing_event.clear()

def testtime():
    started = int(time.time())
    print "Hello %d" % started
    timing_event.wait()
    return '%d %d %d' % (init_time, started, int(time.time()))


class LastQueueUpdate(object):
    def __init__(self, queue_id=0, update=None):
        self.event = Event()
        if update:
            self.update = update
        else:
            self.update = QueueUpdate.objects.filter(queue__id=queue_id).order_by('-id')[0]

class QueueManager(object):
    
    def __init__(self):
        self.updates = {}
        queue_ids = Queue.objects.all().values_list('id')
        for queue_id in queue_ids:
            try:
                self.updates[queue_id[0]] = LastQueueUpdate(queue_id=queue_id[0])
            except:
                update = QueueUpdate(queue=Queue.objects.get(id=queue_id[0]),
                                     timestamp = int(time.time()),
                                     kind = QueueUpdate.EDIT,
                                     kind_id = 1)
                self.updates[queue_id[0]] = LastQueueUpdate(update=update)

    def edit(self, user, queue, room_idlist, draw):
        # Perform the work
        rooms = []
        print 'edit', room_idlist
        for roomid in room_idlist:
            room = Room.objects.get(pk=roomid)
            if (not room) or not draw in room.building.draw.all():
                return json_response({'error':'bad room/draw'})
            rooms.append(room)
        # Clear out the old list
        queue.queuetoroom_set.all().delete()
        # Put in new relationships
        for i in range(0, len(rooms)):
            qtr = QueueToRoom(queue=queue, room=rooms[i], ranking=i)
            qtr.save()
        
        update = QueueUpdate(queue=queue, timestamp=int(time.time()), 
                              kind=QueueUpdate.EDIT, kind_id=user.id)
        update.save()
        self.updates[queue.id].update = update
        self.updates[queue.id].event.set()
        self.updates[queue.id].event.clear()
        room_list = []
        for room in rooms:
            room_list.append({'id':room.id, 'number':room.number,
                              'building':room.building.name})
        return json_response({'rooms':room_list})

    def check(self, user, queue, timestamp):
        print user, queue, timestamp
        latest = self.updates[queue.id]
        if timestamp != 0 and timestamp > latest.update.timestamp:
            print 'going to wait'
            print latest.update.timestamp
            latest.event.wait()
            latest = self.updates[queue.id]
        print 'past wait'
        queueToRooms = QueueToRoom.objects.filter(queue=queue).order_by('ranking')
        if not queueToRooms:
            return json_response({'timestamp':int(time.time()), 'rooms':[]})
        room_list = []
        for qtr in queueToRooms:
            room_list.append({'id':qtr.room.id, 'number':qtr.room.number,
                              'building':qtr.room.building.name})
        return json_response({'timestamp':int(time.time()), 'rooms':room_list})

#if 'IS_REAL_TIME_SERVER' in os.environ:
manager = QueueManager()

check = manager.check
edit = manager.edit


def json_response(value, **kwargs):
#    kwargs.setdefault('content_type', 'text/javascript; charset=UTF-8')
    response =  HttpResponse(simplejson.dumps(value), **kwargs)
    response['Access-Control-Allow-Origin'] =  NORMAL_ADDR
    response['Access-Control-Allow-Credentials'] =  "true"
    response['Access-Control-Allow-Methods'] =  "JSON"
    return response

