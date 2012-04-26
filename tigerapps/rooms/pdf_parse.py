# Utility script to read buildings and draws from the floor plans page and
# put them in the database.
# To run, need to set PYTHONPATH environment variable to point to tigerapps.

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import Tag
from string import strip, rsplit, split

from django.core.management import setup_environ
import settings
setup_environ(settings)

from rooms.models import Draw, Building

floor_terms = {"Ground Floor":0, "First Floor":1, "Second Floor":2, "Third Floor":3,
               "Fourth Floor":4, "Fifth Floor":5, "Sixth Floor":6, "A Level":-1,
               "Lower Floor":-1, "Third Floor Mezzanine":4, "Fourth Floor Mezzanine":5}

# # Regexps for pulling components

# #Building name
# name_pat = re.compile(r'<li class="liOpen"><span class="bullet">&nbsp;(.+)\s*</span><ul>')
# #r'<li class="liOpen"><span class="bullet">&nbsp;(.+)\s</span><ul>')


# #Floor name, file
# floor_pat = re.compile(r'<li class="liBullet"><span class="bullet">&nbsp;</span><a href="https://facilities.princeton.edu/housing/u/floorplans/UnderGrad_dorms/([0-9]{4}-[\w]+).pdf" target="_blank">([^<]+)</a></li>')


# contents = open("pdfpage_files/menu3.html", "r").read()


# name_matches = re.findall(name_pat, contents)

# floor_matches = re.findall(floor_pat, contents)

# print name_matches

f = open("menu3.html", "r")
soup = BeautifulSoup(f)

drawtags = soup.find(id="tree1")

drawtag = drawtags.contents[0]

print "bldgByPdf = [];"
print "pdfByBldg = [];"

while drawtag:
    if not type(drawtag) is Tag:
        drawtag = drawtag.nextSibling
        continue
    drawname = split(drawtag.b.string)[0]
    draw = Draw.objects.get(name=drawname)
    #print draw
    buildingtag = drawtag.ul.li

    while buildingtag:
        if not type(buildingtag) is Tag:
            buildingtag = buildingtag.nextSibling
            continue
        buildingname = buildingtag.span.string[6:].strip()
        try:
            building = Building.objects.get(pdfname=buildingname)
        except:
            building = Building(name = buildingname, pdfname=buildingname,
                                availname = "", lat = 0.0, lon = 0.0)
            building.save()
        building.draw.add(draw)
        
        #print '\t%s' % building
        print "pdfByBldg['%s'] = [];" % building.name
        floors = buildingtag.findAll('a')
        for floor in floors:
             fname = rsplit(floor['href'],'/',1)[1]
             num = floor_terms[floor.string.strip()]

             pdfid = rsplit(fname, ".", 1)[0]
             print "bldgByPdf['%s'] = { building: '%s', floornum : %d };" % (pdfid, building.name, num)
             print "pdfByBldg['%s']['%d'] = '%s';" % (building.name, num, pdfid)
        buildingtag = buildingtag.nextSibling

    drawtag = drawtag.nextSibling
            
            
#print Draw.objects.all()
#print Draw.objects.get(name="Butler")
