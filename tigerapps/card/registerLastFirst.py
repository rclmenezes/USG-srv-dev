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
    names = line.split(",")
    last_name = names[0].capitalize()
    first_name = names[1].split("\n")[0].capitalize()
    #print first_name + " " + last_name
    try:
        m = Member.objects.get(first_name=first_name, last_name=last_name, year__lt=2014)
        m.club = club
        m.is_active = True
        #m.save()
    except:
        print first_name + " " + last_name