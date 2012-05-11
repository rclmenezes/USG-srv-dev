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

    def edit(self, user, queue, room_idlist):
        # Perform the work
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
        
        update = QueueUpdate(queue=queue, timestamp=int(time.time()), 
                              kind=QueueUpdate.EDIT, kind_id=user.id)
        update.save()
        self.updates[queue.id].update = update
        self.updates[queue.id].event.set()
        self.updates[queue.id].event.clear()
        return HttpResponse(rooms)

    def check(self, user, queue, timestamp):
        latest = self.updates[queue.id]
        if timestamp != 0 and timestamp > latest.update.timestamp:
            latest.event.wait()
            latest = self.updates[queue.id]
        queueToRooms = QueueToRoom.objects.filter(queue=queue).order_by('ranking')
        if not queueToRooms:
            return HttpResponse('')
        room_list = []
        for qtr in queueToRooms:
            room_list.append(qtr.room)
        return render_to_response('rooms/queue.html', {'room_list':room_list})

#if 'IS_REAL_TIME_SERVER' in os.environ:
manager = QueueManager()

check = manager.check

def create_message(from_, body):
    data = {'id': str(uuid.uuid4()), 'from': from_, 'body': body}
    data['html'] = render_to_string('message.html', dictionary={'message': data})
    return data


def json_response(value, **kwargs):
    kwargs.setdefault('content_type', 'text/javascript; charset=UTF-8')
    return HttpResponse(simplejson.dumps(value), **kwargs)

