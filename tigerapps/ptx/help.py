# Create your views here.

from django.http import HttpResponse
from django.http import QueryDict
from django.db.models import Q
from ptx.models import Book
from ptx.ptxlogin import getlogstatus
from ptx.navbar import getnavbar
from ptx.ptxrender import render_to_response

def help(request):
	# by default, open Site Overview
    click1 = True
    click2 = False
    dict = {'click1': click1, 'click2': click2}

    # Render to template
    return render_to_response(request, 'ptx/help.html', dict)
