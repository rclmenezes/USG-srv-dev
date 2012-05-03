# makeJSON.py
#
# python makeJSON.py <csv_file> <output_file>

import json
import sys

#################
zoomLevel = '4'
#################

csv_file = sys.argv[1]
out_file = sys.argv[2]

csv = open(csv_file)

bldgsTile = {}
bldgsInfo = {}

def addPtToTile(x, y, code):
    tileX = int(x/256)
    tileY = int(y/256)
    s = zoomLevel + '-' + str(tileX) + '-' + str(tileY)
    if s not in bldgsTile: bldgsTile[s] = set()
    bldgsTile[s].add(zoomLevel + '-' + code)
    

for line in csv:
    fields = [f for f in line.split(',') if f != '']
    x0 = int(fields[1])
    y0 = int(fields[2])
    width = int(fields[3])
    height = int(fields[4])
    x1 = x0 + width
    y1 = y0 + height
    code = fields[5]
    zIndex = int(fields[6])
    
    bldgsInfo[code] = {'height':height, 'width':width, 'left':x0, 'top':y0, 'zIndex': zIndex}
    addPtToTile(x0, y0, code)
    addPtToTile(x0, y1, code)
    addPtToTile(x1, y0, code)
    addPtToTile(x1, y1, code)

for tile in bldgsTile:
    bldgsTile[tile] = list(bldgsTile[tile])
outputDict = {'bldgsTile': bldgsTile, 'bldgsInfo': bldgsInfo}

out = open(out_file, 'w')
out.write(json.dumps(outputDict, indent=4))

