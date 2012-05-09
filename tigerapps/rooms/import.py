import pickle

from django.core.management import setup_environ
import settings
setup_environ(settings)

from rooms.models import Building, Room

roomfile = open('oldrooms.dat')
rooms = pickle.load(roomfile)

mapfile = open('reversemap.dat')
reversemap = pickle.load(mapfile)

for room in rooms:
    try:
        building = Building.objects.get(pk= reversemap[room['buildingname']])
        continue
    except:
        print room['buildingname']
        continue
    # Check that we aren't doubling
    if building.name not in ['Main', 'Bogle', 'North B', 'North C']:
        continue
    roomobj = Room(number = room['number'],
                   sqft = room['sqft'],
                   occ = room['occ'],
                   subfree = room['subfree'],
                   numrooms = room['numrooms'],
                   floor = room['floor'],
                   gender = room['gender'],
                   avail = room['avail'],
                   adjacent = room['adjacent'],
                   ada = room['ada'],
                   bi = room['bi'],
                   con = room['con'],
                   bathroom = room['bathroom'],
                   building = building)
    roomobj.save()
    print room['number'], building




