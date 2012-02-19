import sys, os, traceback
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"
from app.models import User
from sets import Set
from operator import itemgetter
from csv import *


field = 'user_highschool'

uniques =  Set(User.objects.values_list(field,flat=True))	

dict = []
for u in uniques:
	kwargs = {field: u,}
	dict.append( (u, User.objects.filter(**kwargs).count()))
	#print '%d : %s' % (dict[u],u)
dict2 = sorted(dict,key=itemgetter(1))
print dict2
	
output = open( "hist-%s.csv" % (field), "wb", )
csvwriter = writer(output,delimiter=',' )
for s in dict2:
	csvwriter.writerow(s)
