from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.mail import send_mail
from storage.models import *
from storage.forms import *
from django_cas.decorators import login_required, user_passes_test

def paypal(request):
    return HttpResponse('0')
