import json
import pickle

from django.core.management import setup_environ
import settings
setup_environ(settings)

from rooms.models import Building

# f = open("map.json")

# mapobj = json.loads(f.read())

# locs = mapobj['location']

# aliases = {}

# for loc in locs:
#     names =  loc['aliases']
#     names.insert(0, loc['name'])
#     for name in names:
#         try:
#             bldg = Building.objects.get(name=name)
#             if not bldg.pdfname in names:
#                 names.append(bldg.pdfname)
#             aliases[bldg.id] = names    
#             break
#         except:
#             continue

aliases = json.loads(open("aliases.json").read())

reversemap = {}

for pk in aliases:
    for name in aliases[pk]:
        if name in reversemap:
            reversemap[name] = 0
        else:
            reversemap[name] = pk

# for name in reversemap:
#     if reversemap[name] == 0:
#         del reversemap[name]

# Clear out repeats
for pk in aliases:
    for name in aliases[pk]:
        if name in reversemap and reversemap[name] == 0:
            del reversemap[name]

dumpfile = open('reversemap.dat', 'w')
pickle.dump(reversemap, dumpfile, 1)

# for pk in aliases:
#     print pk,
#     for name in aliases[pk]:
#         print name,
#     print

# for bldg in Building.objects.all():
#     if not bldg.id in aliases:
#         print bldg

print json.dumps(aliases, indent=4)
