# cut.py
#
# python cut.py <image_file> <csv_file> <suffix> <output_folder>


import sys
import json
from PIL import Image

#######################
zoomLevel = '4'
ext = '.png'
#######################

image_file = sys.argv[1]
csv_file = sys.argv[2]
suffix = sys.argv[3]
out_folder = sys.argv[4]

image = Image.open(image_file)
csv = open(csv_file, 'r')

for line in csv:
    fields = [f for f in line.split(',') if f != '']
    x0 = int(fields[1])
    y0 = int(fields[2])
    x1 = x0 + int(fields[3])
    y1 = y0 + int(fields[4])
    code = fields[5].rstrip()
    cut = image.crop((x0, y0, x1, y1))
    filename = out_folder + zoomLevel + '-' + code + '-' + suffix + ext
    print(filename)
    cut.save(filename)

csv.close()
    


    
