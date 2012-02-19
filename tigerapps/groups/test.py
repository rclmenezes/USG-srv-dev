from globalsettings import SITE_URL,SITE_EMAIL
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db.models import Q
from rss import *
from models import *
from views import *
from forms import *


def login(request):

    if request.method == 'POST':
        if 'netid' in request.POST:
            s = Student.objects.get(netid=request.POST['netid'])
            request.session['user'] = s
            return redirect_index(request)
    
    return render_to_response('groups/test.html')
    

                                   
