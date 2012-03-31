from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.core.paginator import Paginator
from django.core.mail import send_mail
from ccc.models import *
from ccc.forms import *

def index(request):
    return render_to_response('pom/index.html')

