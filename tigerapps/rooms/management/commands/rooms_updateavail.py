from django.core.management.base import BaseCommand, CommandError
from tigerapps.rooms.models import *
from tigerapps.rooms.update import *
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
        updateavail(roomset)
        


    def pastupdate(self, num):
        return
