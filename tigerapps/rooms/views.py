# Create your views here.
#from django.http import HttpResponse
from django.shortcuts import render_to_response
#from rooms.models import Poll
from django.contrib.auth.decorators import login_required, user_passes_test
from models import Draw, Building, Room
import json

@login_required
def index(request):
    draw_list = Draw.objects.order_by('name')
    building_list = Building.objects.order_by('name')
    #buildingbydraw_dict = {}
    #for draw in draw_list:
        #buildingbydraw_dict[draw] = Building.objects.filter(draw__name=draw)
    #    buildingbydraw_dict[draw] = Building.objects
    room_list = Room.objects.order_by('number')
    mapscript = mapdata()
    return render_to_response('rooms/base_dataPanel.html', locals())


def mapdata():
    buildings = Building.objects.order_by('id')
    maplist = []
    for building in buildings:
        maplist.append({'name':building.name, 'lat':building.lat, 'lon':building.lon})
    mapstring = json.dumps(maplist)
    mapscript = '<script type="text/javascript">mapdata = %s</script>' % mapstring
    return mapscript
