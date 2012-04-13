# Script for updating building latitude and longitude values 
# using OIT's online information feed. List of feeds are available
# at http://etcweb.princeton.edu/MobileFeed as of April 12, 2012. 
# To run, need to set PYTHONPATH environment variable to point to tigerapps.

from django.core.management import setup_environ
import settings
setup_environ(settings)

import json
import urllib2
from rooms.models import Draw, Building

# open info feed
f = urllib2.urlopen('http://etcweb.princeton.edu/MobileFeed/map/?fmt=json')
obj = json.load(f)

# info feed has two immediate children: location and timestamp
locations = obj['location']

for location in locations:

	# build list of potential names for this building
	names = []
	names.append(location['name']);
	for alias in location['aliases']:
		names.append(alias);
		
	for n in names:
		try:
			# see if building is in database
			building = Building.objects.get(name=n)

			# if so, update with values from feed
			building.lat = location['latitude']
			building.lon = location['longitude']
			building.save()

			break

		except:
			continue