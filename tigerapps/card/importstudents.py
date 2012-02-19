########## Essential for script
import sys,os
sys.path.insert(0,os.path.abspath("/srv/tigerapps"))
import settings
from django.core.management import setup_environ
setup_environ(settings)
###########

from card.models import Member

f = open(sys.argv[1])
for line in f:
   info = line.split(",")
   
   puid = info[0]
   first_name = info[1]
   last_name = info[3]
   year = info[6]
   netid = info[16].split("@")[0]
   access = 'M'
   
   if len(info) != 19:
       print line
       continue
   
   if len(netid) > 8 or len(netid) == 1:
       print line
       continue

   try:
       m = Member.objects.get(netid=netid)  
   except Member.DoesNotExist:
       m = Member()
       m.puid = puid
       m.first_name = first_name
       m.last_name = last_name
       m.year = year
       m.netid = netid
       try:
           m.save()
       except:
           print line
   