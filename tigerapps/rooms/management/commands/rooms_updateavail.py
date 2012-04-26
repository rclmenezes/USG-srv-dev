from django.core.management.base import BaseCommand, CommandError
from tigerapps.rooms.models import *
from django.core.mail import send_mail
import random

class Command(BaseCommand):
    args = '<random|past|real [num]>'
    help = 'Mark newly unavailable rooms as such. Testing:random,past.'

    def handle(self, *args, **options):
        updatetype = args[0]
        num = 0
        if (len(args) > 1):
            num = int(args[1])
        if updatetype == 'random':
            self.randomupdate(num)

    def randomupdate(self, num):
        left = Room.objects.filter(avail=True).values_list('id',flat=True)
        if not left:
            return
        # self.stdout.write('%s\n' % left)
        if (num < len(left)):
            taken = random.sample(left, num)
        else:
            taken = left
        roomset = Room.objects.filter(id__in=taken)
        self.update(roomset)

    def pastupdate(self, num):
        return

    # Mark a collection of rooms as taken and notify people as necessary
    def update(self, roomset):
        # Mark as taken
        roomset.update(avail=False)
        
        for room in roomset:
            self.notify(room)

    def notify(self, room):
        qids = QueueToRoom.objects.filter(room=room).values_list('queue_id',flat=True)
        queues = Queue.objects.filter(id__in=qids)
        users = User.objects.filter(queues__in=queues).distinct()
        #self.stdout.write('%s\n' % users)
        for user in users:
            self.email(user, room)

    def email(self, user, room):
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

