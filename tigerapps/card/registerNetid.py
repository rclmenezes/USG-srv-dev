########## Essential for script
import sys,os
sys.path.insert(0,os.path.abspath("/srv/tigerapps"))
import settings
from django.core.management import setup_environ
setup_environ(settings)
###########

from card.models import Member, Club

club = Club.objects.get(name=sys.argv[1])
f = open(sys.argv[2])
for line in f:
   netid = line.split('\n')[0]
   try:
       m = Member.objects.get(netid=netid)
       m.club = club
       m.is_active = True
       #m.save()
   except Member.DoesNotExist:
       print netid
