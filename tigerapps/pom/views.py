from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.core.paginator import Paginator
from django.core.mail import send_mail
from ccc.models import *
from ccc.forms import *
import datetime

def index(request, offset):
    if offset != '':
        try:
            offset = int(offset)
        except:
            raise Http404()
        current_time = datetime.datetime.now() + datetime.timedelta(hours=offset)
    else:
        current_time = datetime.datetime.now()
    
    return render_to_response('pom/index.html', {'current_time': current_time})

