# Create your views here.
#from django.http import HttpResponse
from django.shortcuts import render_to_response
#from rooms.models import Poll

def index(request):
    return render_to_response('rooms/base.html')


