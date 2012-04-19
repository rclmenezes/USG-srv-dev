# Create your views here.
# from django.http import HttpResponse
from django.shortcuts import render_to_response
# from rooms.models import Poll
from django.contrib.auth.decorators import login_required, user_passes_test
from models import Draw, Building, Room
import json

@login_required
def index(request):
    draw_list = Draw.objects.order_by('id')
    mapscript = mapdata()
    return render_to_response('rooms/base_dataPanel.html', locals())

@login_required
def draw(request, drawid):
    room_list = Room.objects.filter(building__draw__id=drawid)
    return render_to_response('rooms/drawtab.html', locals())

def mapdata():
    buildings = Building.objects.order_by('id')
    maplist = []
    for building in buildings:
        draws = []
        for draw in building.draw.all():
            draws.append(draw.id)
        maplist.append({'name':building.name, 'draws':draws,
                        'lat':building.lat, 'lon':building.lon})
    mapstring = json.dumps(maplist)
    mapscript = '<script type="text/javascript">mapdata = %s</script>' % mapstring
    return mapscript
