# Create your views here.
#from django.http import HttpResponse
from django.shortcuts import render_to_response
#from rooms.models import Poll
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
def index(request):
    return render_to_response('rooms/base.html')


