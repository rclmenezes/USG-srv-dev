from tigerapps.rooms.models import *
from django.core.mail import send_mail



    # Mark a collection of rooms as taken and notify people as necessary
def updateavail(roomset):
    # Mark as taken
    roomset.update(avail=False)
    
    for room in roomset:
        notify(room)

def notify(room):
    qids = QueueToRoom.objects.filter(room=room).values_list('queue_id',flat=True)
    queues = Queue.objects.filter(id__in=qids)
    users = User.objects.filter(queues__in=queues).distinct()
    #self.stdout.write('%s\n' % users)
    for user in users:
        if user.do_email:
            email(user, room)
        if user.do_text and user.confirmed:
            text(user, room)

def email(user, room):
    subject = 'Rooms: %s Taken' % room
    content = '''%s was on your room draw queue, and was taken.

You are receiving this message because you have email queue notifications turned on.
To disable, go to rooms.tigerapps.org.
Please do not respond to this email, it is from an unmonitored email address.

Thanks,
The Rooms Team
''' % room
    send_mail(subject, content, 'rooms@tigerapps.org',
              ['%s@princeton.edu' % user.netid], fail_silently=False)

def text(user, room):
    content = "The room %s is no longer available. Oh no!" % room
    send_mail("", content, 'room@tigerapps.org',
              ['%s@%s' % (user.phone, user.carrier.address)], fail_silently=False)
